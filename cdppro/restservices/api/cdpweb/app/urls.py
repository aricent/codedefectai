from django.urls import path
from .views import projects, prediction_listings

urlpatterns = [path(r'rest/api/system/projects/meta', projects, name='Projects'),
    path(r'rest/api/project/(?P<project_id>\d+)/predictions', prediction_listings, name='Predictions'),]
