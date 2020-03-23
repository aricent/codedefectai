"""
Definition of urls for cdpweb.
"""

from app import views
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path
#from rest_framework_swagger.views import get_swagger_view
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

#schema_view = get_swagger_view(title='Code Defect Prediction API')
schema_view = get_schema_view(title='Code Defect Prediction API', url="/pastebin", renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    url(r'^$', schema_view),
    url(r'rest/api/system/projects/meta', views.projects, name='Projects'),
    url(r'rest/api/project/(?P<project_id>\d+)/predictions', views.prediction_listings, name='Predictions'),
    url(r'rest/api/project/(?P<project_id>\d+)/commit/(?P<commit_id>\w+)/$', views.prediction_listings_for_commit,
        name='PredictionsForCommit'),
    url(r'rest/api/project/(?P<project_id>\d+)/commit/(?P<commit_id>\w+)/filename/(?P<file_name>.*)/explaination',
        views.lime_analysis, name='LimeAnalysis'),
    url(r'rest/api/project/(?P<project_id>\d+)/trend', views.trend_analysis, name='TrendAnalysis')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)