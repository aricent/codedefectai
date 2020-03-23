"""
Definition of views.
"""
import json
import time
from collections import OrderedDict
from datetime import datetime, timedelta

from django.db.models import Count
from django.utils.functional import cached_property
from django.views.decorators.gzip import gzip_page
from html5lib import serializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .testdbconnection import TestDbConnecton
from .models import Projects, Projectsummary, Explainablecdp, Predictionlisting, Predctionfeaturetrend
from .serializers import ProjectsSerializer, PredictionlistingSerializer
from .prepareresult import PrepareResult
import os
import pandas as pd

db_server = "default"

days = 15

projects_constant = {1: "spring-projects/spring-boot", 2: "opencv/opencv", 3: "dotnet/corefx"}


def get_projects(dbserver):
    project_list = []
    queryset = Projects.objects.using(dbserver).all()
    data = queryset.values("id", "projectname", "codinglanguage", "description")

    project_df = pd.DataFrame(data)
    queryset = Projectsummary.objects.using(dbserver).all()

    summary = queryset.values("projectid", "totalfilesforprediction", "totalcommitsforprediction", "buggypredictions")

    project_summary_df = pd.DataFrame(summary)

    project_df = pd.merge(project_df, project_summary_df, how="left", left_on=["id"], right_on=["projectid"])

    project_df = project_df[
        ["id", "projectname", "codinglanguage", "totalfilesforprediction", "totalcommitsforprediction",
         "buggypredictions"]]
    project_df.columns = ["Id", "ProjectName", "CodingLanguage", "TotalFilesForPrediction", "TotalCommitsForPrediction",
                          "BuggyPredictions"]

    result = {"projectList": project_df.to_dict(orient='records')}
    data = {"response": "success", "result": result}
    return data


@gzip_page
@api_view(["GET"])
def projects(request):
    """
    Get:
    Return a list of all the existing projects.
    """
    global db_server
    if request.method == 'GET':
        try:
            data = get_projects(db_server)
        except Exception as e:
            print(f"failed to get data from {db_server}. Exception: {e.__traceback__}")
            testdbconnection = TestDbConnecton()
            db_server = testdbconnection.get_db_server()
            try:
                data = get_projects(db_server)
            except Exception as e:
                print(f"failed to get data from {db_server}. Exception: {e.__traceback__}")
                return JsonResponse({"response": "Error Occurred. Please try again after sometime...!!!"})

        return JsonResponse(data, status=200)
    else:
        data = {
            "error": True,
            "errors": serializer.errors,
        }
        return Response({"error": data, "error": True})


def get_prediction_listing(request, dbserver, project_id):
    global projects_constant
    # queryset = Projects.objects.using(dbserver).filter(id=project_id)
    # data = queryset.values("githubprojectname")
    project_name = None
    project_name = projects_constant.get(int(project_id))

    if project_name is not None and len(project_name) == 0:
        return {"response": f"No data available for project id {project_id}"}

    sort_constant = {"commitId": "commit_id", "timestamp": "timestamp", "prediction": "prediction"}

    page = request.GET.get('page', 1)
    items_per_page = request.GET.get('items_per_page', 10)
    sort_type = request.GET.get('sort_type', 'timestamp')
    sort_by = request.GET.get('sort_by', 'desc')

    if sort_by is None or sort_by == '':
        sort_by = "desc"

    try:
        sort_type = sort_constant[sort_type]
    except Exception as ex:
        print(ex)
        response = {"response": "Bad Request"}
        return JsonResponse(response, status=400)

    if sort_by == "desc":
        sort = '-' + sort_type
    else:
        sort = sort_type

    query_date = (datetime.today() - timedelta(days=15)).strftime("%Y-%m-%d")  # %H:%M:%S

    start_time = time.time()

    if sort_type == "prediction":
        queryset = Predictionlisting.objects.using(dbserver).filter(project_id=project_id, timestamp__gte=query_date). \
            values_list("commit_id", "prediction").annotate(total=Count('commit_id')).order_by(sort, '-total')
        data = queryset.values_list("commit_id", "prediction", "total")
        data_df = pd.DataFrame(data, columns=["commit_id", "prediction", "total"])
        data_df = data_df.sort_values(by=["prediction", "total"], ascending=[False, False])
        data_df.reset_index()
        data = data_df["commit_id"].to_list()
        data = list(dict.fromkeys(data))
        if sort_by == "asc":
            data.reverse()
    else:
        queryset = Predictionlisting.objects.using(dbserver).filter(project_id=project_id, timestamp__gte=query_date).order_by(sort).only('commit_id').distinct()
        data = queryset.values_list("predictionlistingid", "commit_id")
        data_df = pd.DataFrame(data, columns=["predictionListingid", "commit_id"])
        data = data_df["commit_id"].to_list()
        data = list(dict.fromkeys(data))

    total_commit_count = len(data)
    paginator = Paginator(data, items_per_page)
    try:
        page_data = paginator.page(page)
        commit_details_queryset = Predictionlisting.objects.using(dbserver).filter(commit_id__in=page_data.object_list)
        data = commit_details_queryset.values("commit_id", "timestamp", "file_name", "file_parent", "prediction",
                                              "confidencescore")
        end_time = time.time()
        print(f"Total Time {end_time - start_time}")
    except PageNotAnInteger:
        return {"response": "Page is not an Integer"}
    except EmptyPage:
        return {"response": ""}

    if len(data) == 0:
        return {"response": ""}
    prepare_result = PrepareResult()
    if page_data.has_next():
        result = prepare_result.prediction_listing_pagination(data, total_commit_count, page_data.object_list,
                                                              sort_type,
                                                              sort_by,
                                                              project_name,
                                                              page_data.number,
                                                              page_data.next_page_number(),
                                                              page_data.paginator.page_range)
    else:
        result = prepare_result.prediction_listing_pagination(data, total_commit_count, page_data.object_list,
                                                              sort_type,
                                                              sort_by,
                                                              project_name,
                                                              page_data.number,
                                                              None, page_data.paginator.page_range)

    return result


@gzip_page
@api_view(["GET"])
def prediction_listings(request, project_id):
    """
    Get:
    Return a list of all the commit predictions for a project.
    """

    global db_server
    if db_server is None or db_server == "":
        db_server = "default"

    if request.method == 'GET':
        start_time = time.time()
        try:
            result = get_prediction_listing(request, db_server, project_id)
        except Exception as e:
            print(f"failed to get data from {db_server}. {e.__traceback__}")
            try:
                testdbconnection = TestDbConnecton()
                db_server = testdbconnection.get_db_server()
                result = get_prediction_listing(request, db_server, project_id)
            except Exception as e:
                return JsonResponse({"response": "Error Occurred. Please try again after sometime...!!!"})

        response = {"response": "success", "result": result}
        end_time = time.time()
        print(f"Total Time {end_time - start_time}")
        return JsonResponse(response, status=200)

    else:
        data = {
            "error": True,
            "errors": serializer.errors,
        }
        return HttpResponse({"Internal Server Error": data, "error": True})


def get_prediction_listing_for_commit(dbserver, project_id, commit_id):
    global projects_constant

    project_name = None
    project_name = projects_constant.get(int(project_id))

    if project_name is not None and len(project_name) == 0:
        return JsonResponse({"response": f"No data available for project id {project_id}"})

    queryset = Predictionlisting.objects.using(dbserver).filter(project_id=project_id, commit_id=commit_id)

    data = queryset.values("commit_id", "timestamp", "file_name", "file_parent", "prediction", "confidencescore")

    if len(data) == 0:
        return JsonResponse({"response": "No data available"})
    prepare_result = PrepareResult()
    result = prepare_result.prediction_listing(data, project_name)

    return result


@gzip_page
@api_view(["GET"])
def prediction_listings_for_commit(request, project_id, commit_id):
    """
    Get:
    Return a list of all the commit predictions for a project.
    """

    global db_server
    if db_server is None or db_server == "":
        db_server = "default"

    if request.method == 'GET':
        try:
            result = get_prediction_listing_for_commit(db_server, project_id, commit_id)
        except Exception as e:
            print(f"failed to get data from {db_server}. {e.__traceback__}")
            try:
                testdbconnection = TestDbConnecton()
                db_server = testdbconnection.get_db_server()
                result = get_prediction_listing_for_commit(db_server, project_id, commit_id)
            except Exception as e:
                return JsonResponse({"response": "Error Occurred. Please try again after sometime...!!!"})

        response = {"response": "success", "result": result}
        return JsonResponse(response, status=200)

    else:
        data = {
            "error": True,
            "errors": serializer.errors,
        }
        return HttpResponse({"Internal Server Error": data, "error": True})


def get_lime_analysis(dbserver, project_id, commit_id, file_name):
    global projects_constant
    project_name = projects_constant.get(int(project_id))

    if project_name is not None and len(project_name) == 0:
        return JsonResponse({"response": f"No data available for project id {project_id}"})

    print("file_name is {}".format(file_name))
    filename = file_name.split("/")[-1]

    fileparent = os.path.split(file_name)[0] + "/"

    queryset = Predictionlisting.objects.using(dbserver).filter(project_id=project_id, commit_id=commit_id,
                                                                file_name=filename, file_parent=fileparent)
    data = queryset.values("predictionlistingid", "prediction", "confidencescore", "timestamp")

    prediction_listings_df = pd.DataFrame(data)
    if len(prediction_listings_df) == 1:
        predictionListtingId = int(prediction_listings_df["predictionlistingid"].to_list()[0])
        confidence_score = float(prediction_listings_df["confidencescore"].to_list()[0])
        confidence_score = "{:.2f}".format(confidence_score * 100)
    else:
        return JsonResponse({"response": "Error: Multiple prediction listing is available..."})

    queryset_explain = Explainablecdp.objects.using(dbserver).filter(predictionlistingid=predictionListtingId)

    data_explain = queryset_explain.values("featurelabel", "featurevalue", "featurecoefficient", "featurekey",
                                           "featurename", "featureunits")

    if len(data) == 0 or len(data_explain) == 0:
        return JsonResponse({"response": "No data available"})
    prepare_result = PrepareResult()
    result = prepare_result.lime_analysis(data_explain, prediction_listings_df, confidence_score, project_name,
                                          commit_id, file_name)
    print(result)
    return result


@gzip_page
@api_view(["GET"])
def lime_analysis(request, project_id, commit_id, file_name):
    """
    Get:
    Return a list of top five features for bug prediction.
    """
    print("project_id:", project_id)

    global db_server
    if db_server is None or db_server == "":
        db_server = "default"

    if request.method == 'GET':
        print(request)
        try:
            # result = get_lime_analysis(db_server, project_id, commit_id, file_name)
            result = get_lime_analysis(db_server, project_id, commit_id, file_name)
        except Exception as e:
            print(f"failed to get data from {db_server}. {e.__traceback__}")
            try:
                test_db_connection = TestDbConnecton()
                db_server = test_db_connection.get_db_server()
                # result = get_lime_analysis(db_server, project_id, commit_id, file_name)
                result = get_lime_analysis(db_server, project_id, commit_id, file_name)
            except Exception as ex:
                print(ex)
                return JsonResponse({"response": "Error Occurred. Please try again after sometime...!!!"})

        return JsonResponse(result, status=200)

    else:
        data = {
            "error": True,
            "errors": serializer.errors,
        }
        return HttpResponse({"Internal Server Error": data, "error": True})


def get_trend_analysis(dbserver, project_id):
    global projects_constant
    project_name = None
    project_name = projects_constant.get(int(project_id))

    if project_name is not None and len(project_name) == 0:
        return JsonResponse({"response": f"No data available for project id {project_id}"})

    trend_query_set = Predctionfeaturetrend.objects.using(db_server).filter(projectid=project_id)
    trend_data = trend_query_set.values("prediction", "featurename", "median", "firstquartile", "thirdquartile",
                                        "minimum", "maximum", "projectid")

    trend_data_df = pd.DataFrame(trend_data)

    if len(trend_data_df) == 0:
        return JsonResponse({"response": "No data available"})
    prepare_result = PrepareResult()
    result = prepare_result.trend_analysis(trend_data_df)

    return result


@gzip_page
@api_view(["GET"])
def trend_analysis(request, project_id):
    """
    Get:
    Return a list of top five features for bug prediction.
    """
    print("project_id:", project_id)

    global db_server
    if db_server is None or db_server == "":
        db_server = "default"

    if request.method == 'GET':
        try:
            result = get_trend_analysis(db_server, project_id)
        except Exception as e:
            print(f"failed to get data from {db_server}. {e.__traceback__}")
            try:
                testdbconnection = TestDbConnecton()
                db_server = testdbconnection.get_db_server()
                result = get_trend_analysis(db_server, project_id)
            except Exception as e:
                print(e)
                return JsonResponse({"response": "Error Occurred. Please try again after sometime...!!!"})

        response = result
        return JsonResponse(response, status=200)
    else:
        data = {
            "error": True,
            "errors": serializer.errors,
        }
        return HttpResponse({"Internal Server Error": data, "error": True})
