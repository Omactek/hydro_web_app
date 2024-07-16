from rest_framework import serializers
from hydro import models as hydro_models
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class StationGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = hydro_models.StationMetadata
        geo_field = 'geom'
        fields = ['st_name', 'st_label', 'geom']

class StationMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = hydro_models.StationMetadata
        fields = ['st_name', 'st_label']

class ValuesMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = hydro_models.ValuesMetadata
        fields = ['django_field_name', 'parameter', 'unit']
