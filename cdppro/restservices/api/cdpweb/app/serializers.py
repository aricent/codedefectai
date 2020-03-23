
from rest_framework import serializers
from .models import Explainablecdp, Predictionlisting, Predictionrawdata, Projects, Projectsummary


class ExplainablecdpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Explainablecdp
        fields = '__all__'

class PredictionlistingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Predictionlisting
        fields = '__all__'

class PredictionrawdataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Predictionrawdata
        fields = '__all__'

class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = '__all__'
 
class ProjectsummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Projectsummary
        fields = '__all__'

