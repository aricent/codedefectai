import time
from itertools import islice
import pandas as pd


class PrepareResult:
    """description of class"""

    def __init__(self, ):
        pass

    def calculator(self, row):
        if row["coefficient"] == 0:
            value = row["values"] * -1
        else:
            value = row["values"]
        return value

    def prediction_listing(self, data, project_name):
        preds_list = []
        prediction_listing = []
        counter = 0
        header = "https://github.com"

        prediction_df = pd.DataFrame(data)

        prediction_df["file_name"] = prediction_df["file_parent"] + prediction_df["file_name"]
        prediction_df["file_link"] = f"{header}/{project_name}/blob"
        prediction_df["file_link"] = prediction_df[["file_link", "commit_id", "file_name"]].apply(
            lambda row: f'{row.file_link}/{row.commit_id}/{row.file_name}', axis=1)

        prediction_df = prediction_df.sort_values("commit_id", ascending=True)
        prediction_df = prediction_df.reset_index()

        prev_commitid = None
        for index in prediction_df.index:
            row = prediction_df.loc[index]
            commitid = row["commit_id"]

            if index == 0:
                prev_commitid = commitid

            prediction = {
                "file_name": row["file_name"],
                "timestamp": str(row["timestamp"]),
                "prediction": int(row["prediction"]),
                "confidencescore": "{:.2f}".format(row["confidencescore"] * 100),
                "file_link": row["file_link"]
            }

            preds_list.append(prediction)

        predictions = {"commitId": prev_commitid, "count":
            str(prediction_df.shape[0]), "preds": list(preds_list)}
        prediction_listing.append(predictions)

        result = {"project_name": project_name, "predictionListing": list(prediction_listing)}

        return result

    def prediction_listing_pagination(self, data, total_commit_count, commit_id_list, sort_type, sort_by, project_name,
                                      current_page,
                                      next_page, total_page):

        preds_list = []
        prediction_listing = []
        # counter = 0
        header = "https://github.com"

        start_time = time.time()
        prediction_df = pd.DataFrame(data)

        for commit_id in commit_id_list:
            prediction_df_sub_frame = prediction_df.loc[prediction_df["commit_id"] == commit_id]
            if sort_type == "prediction":
                if sort_by == "desc":
                    prediction_df_sub_frame = prediction_df_sub_frame.sort_values("prediction", ascending=False)
                else:
                    prediction_df_sub_frame = prediction_df_sub_frame.sort_values("prediction", ascending=True)

            prediction_df_sub_frame = prediction_df_sub_frame.reset_index()
            # count = 0
            for index in prediction_df_sub_frame.index:
                if index < 5:
                    prediction = {
                        "file_name": prediction_df_sub_frame.loc[index, "file_parent"] + prediction_df_sub_frame.loc[
                            index, "file_name"],
                        "timestamp": str(prediction_df_sub_frame.loc[index, "timestamp"]),
                        "prediction": int(prediction_df_sub_frame.loc[index, "prediction"]),
                        "confidencescore": "{:.2f}".format(prediction_df_sub_frame.loc[index, "confidencescore"] * 100),
                        "file_link": f'{header}/{project_name}/blob/{commit_id}/{prediction_df_sub_frame.loc[index, "file_parent"]}/{prediction_df_sub_frame.loc[index, "file_name"]}'
                    }

                    preds_list.append(prediction)
                # count = count + 1

            predictions = {"commitId": commit_id, "total_count": int(prediction_df_sub_frame.shape[0]),
                           "prediction_count": int(len(prediction_df_sub_frame[prediction_df_sub_frame["prediction"] == 1])),
                           "preds": list(preds_list)}
            prediction_listing.append(predictions)
            preds_list = []

        result = {"project_name": project_name, "total_commit_count": total_commit_count,
                  "predictionListing": list(prediction_listing),
                  "current_page": current_page, "next_page": next_page, "page_range": (total_page.stop - 1)}
        end_time = time.time()
        print(f"Total Time {end_time - start_time}")
        return result

    def lime_analysis(self, data_explain, data, confidence_score, project_name, commit_id, file_name):
        print("inside lime analysis prepare result")
        header = "https://github.com/"
        data_explain_df = pd.DataFrame(data_explain)

        data_explain_df = data_explain_df.sort_values("featurecoefficient", ascending=False)
        df = data_explain_df.reset_index()
        # print("df = {}".format(df))
        features_list = []
        for index in df.index:  # islice(df.iterrows(), 5):
            row = df.loc[index]
            if index < 5:
                temp_json = {
                    "name": row["featurename"],
                    "key": row["featurekey"],
                    "label": int(row["featurelabel"]),
                    "value": int(row["featurevalue"]),
                    "unit": row["featureunits"],
                    "coefficient": float(row["featurecoefficient"])
                }
                features_list.append(temp_json)

        # file_link = f"{header}/{project_name}/commits/{commit_id}/{file_name}"
        file_link = f"{header}/{project_name}/commits/master/{file_name}"
        result = {"commitId": commit_id, "timeStamp": str(data["timestamp"].to_list()[0]), "fileName": file_name,
                  "prediction": data["prediction"].to_list()[0], "file_link": file_link,
                  "confidencescore": confidence_score, "features": features_list}

        result = {"response": "success", "result": result}

        return result

    def trend_analysis(self, data):

        trend_df = pd.DataFrame(data)
        result = {}
        feature_label = [0, 1]
        for feature in feature_label:
            trend_df_prediction = trend_df.loc[trend_df["prediction"] == feature]
            trend_df_prediction = trend_df_prediction.sort_values("median", ascending=False)
            trend_df_prediction = trend_df_prediction.reset_index()
            feature_result = []
            for index in trend_df_prediction.index:
                if index < 5:
                    row = trend_df_prediction.loc[index]
                    temp_json = {
                        "name": str(row["featurename"]),
                        "median": str(row["median"]),
                        "firstQuartile": str(row["firstquartile"]),
                        "thirdQuartile": str(row["thirdquartile"]),
                        "minimum": str(row["minimum"]),
                        "maximum": str(row["maximum"])
                    }
                    feature_result.append(temp_json)
            if feature == 0:
                result["LowBugRisk"] = feature_result
            else:
                result["HighBugRisk"] = feature_result
        result = {"response": "success", "result": result}
        # print(result)
        return result
