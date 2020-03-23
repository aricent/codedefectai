# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Explainablecdp(models.Model):
    explainablecdpid = models.AutoField(db_column='ExplainableCDPId', primary_key=True)  # Field name made lowercase.
    featurename = models.CharField(db_column='FeatureName', max_length=50, blank=True,
                                   null=True)  # Field name made lowercase.
    featurekey = models.CharField(db_column='FeatureKey', max_length=50, blank=True,
                                  null=True)  # Field name made lowercase.
    featurevalue = models.FloatField(db_column='FeatureValue', blank=True, null=True)  # Field name made lowercase.
    featureunits = models.CharField(db_column='FeatureUnits', max_length=10, blank=True,
                                    null=True)  # Field name made lowercase.
    featurelabel = models.IntegerField(db_column='FeatureLabel')  # Field name made lowercase.
    featurecoefficient = models.FloatField(db_column='FeatureCoefficient', blank=True,
                                           null=True)  # Field name made lowercase.
    predictionlistingid = models.ForeignKey('Predictionlisting', models.DO_NOTHING,
                                            db_column='PredictionListingId')  # Field name made lowercase.
    createtimestamp = models.DateTimeField(db_column='CreateTimestamp')  # Field name made lowercase.
    projectid = models.ForeignKey('Projects', models.DO_NOTHING, db_column='ProjectId')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'explainablecdp'


class Predictionlisting(models.Model):
    predictionlistingid = models.AutoField(db_column='PredictionListingId',
                                           primary_key=True)  # Field name made lowercase.
    commit_id = models.CharField(db_column='COMMIT_ID', max_length=50)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='TimeStamp')  # Field name made lowercase.
    file_name = models.CharField(db_column='FILE_NAME', max_length=150)  # Field name made lowercase.
    file_parent = models.CharField(db_column='FILE_PARENT', max_length=255)  # Field name made lowercase.
    file_status = models.CharField(db_column='FILE_STATUS', max_length=10)  # Field name made lowercase.
    prediction = models.IntegerField(db_column='Prediction')  # Field name made lowercase.
    confidencescore = models.FloatField(db_column='ConfidenceScore')  # Field name made lowercase.
    project_id = models.PositiveIntegerField(db_column='Project_Id')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'predictionlisting'


class Predictionrawdata(models.Model):
    predictionrawdataid = models.AutoField(db_column='PredictionRawDataId',
                                           primary_key=True)  # Field name made lowercase.
    day = models.DateField(db_column='DAY')  # Field name made lowercase.
    raw_data = models.TextField(db_column='RAW_DATA', blank=True, null=True)  # Field name made lowercase.
    projectid = models.ForeignKey('Projects', models.DO_NOTHING, db_column='ProjectId')  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='TIMESTAMP')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'predictionrawdata'
        unique_together = (('day', 'projectid'),)


class Predctionfeaturetrend(models.Model):
    featuretrendid = models.AutoField(db_column='FeatureTrendId', primary_key=True)  # Field name made lowercase.
    featurename = models.CharField(db_column='FeatureName', max_length=50)  # Field name made lowercase.
    median = models.FloatField()
    firstquartile = models.FloatField(db_column='firstQuartile')  # Field name made lowercase.
    thirdquartile = models.FloatField(db_column='thirdQuartile')  # Field name made lowercase.
    minimum = models.FloatField()
    maximum = models.FloatField()
    prediction = models.IntegerField(db_column='Prediction')  # Field name made lowercase.
    projectid = models.ForeignKey('Projects', models.DO_NOTHING, db_column='ProjectId')  # Field name made lowercase.
    createtime = models.DateTimeField(db_column='CreateTime')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'predctionfeaturetrend'


class Projects(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    projectname = models.CharField(db_column='ProjectName', max_length=50)  # Field name made lowercase.
    githubprojectname = models.CharField(db_column='GithubProjectName', max_length=50)  # Field name made lowercase.
    codinglanguage = models.CharField(db_column='CodingLanguage', max_length=50)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'projects'


class Projectsummary(models.Model):
    id = models.PositiveIntegerField(db_column='Id', primary_key=True)  # Field name made lowercase.
    projectid = models.ForeignKey(Projects, models.query, db_column='ProjectId')  # Field name made lowercase.
    totalfilesforprediction = models.IntegerField(db_column='TotalFilesForPrediction')  # Field name made lowercase.
    totalcommitsforprediction = models.IntegerField(db_column='TotalCommitsForPrediction')  # Field name made lowercase.
    buggypredictions = models.IntegerField(db_column='BuggyPredictions')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'projectsummary'
