from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models.functions import ExtractYear
from .serializers import StationMetadataSerializer, ValuesMetadataSerializer, StationGeoSerializer
from hydro import models as hydro_models
from django.apps import apps
from django.shortcuts import render
from datetime import date
from rest_framework.exceptions import ValidationError
from .utils import prepare_data_for_chart
from django.utils.html import escape

class ValuesMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = hydro_models.ValuesMetadata.objects.all()
    serializer_class = ValuesMetadataSerializer

class StationMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = hydro_models.StationMetadata.objects.all()
    serializer_class = StationMetadataSerializer

    @action(detail=True, methods=['get']) #returns parameters for selected station
    def values(self, request, pk=None): #request used for decorator, pk for specific station instance
        station = self.get_object()
        model = self.get_model_from_table(station.st_name)
        fields = [field.name for field in model._meta.fields]
        values = hydro_models.ValuesMetadata.objects.filter(django_field_name__in=fields)
        serializer = ValuesMetadataSerializer(values, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get']) #returns all years of selected station measurements to keep number of requests lower
    def years(self, request, pk=None):
        station = self.get_object()
        model = self.get_model_from_table(station.st_name)
        years = sorted(model.objects.annotate(year=ExtractYear('date_time')).values_list('year', flat=True).distinct())
        return Response(years)
    
    @action(detail=False, methods=['get']) #returns geojson
    def geo(self, request):
        serializer = StationGeoSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get']) #returns all data for selected stations (/api/stations/<station_id>/data/), not used in front end currently
    def data(self, request, pk=None):
        station = self.get_object()
        model = self.get_model_from_table(station.st_name)
        data = model.objects.values()
        return Response(data)

    @staticmethod
    def get_model_from_table(table_name):
        for model in apps.get_models():
            if model._meta.db_table == table_name:
                return model
        raise ValueError('No model found with db_table {}!'.format(table_name))

@api_view(['GET'])
def yearly_chart_data(request, station_id, field, year):
    model = StationMetadataViewSet.get_model_from_table(station_id)
    year = int(year)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    data = model.get_field_data(field, start_date, end_date)
    return Response(data)

@api_view(['GET'])
def get_percentiles(request, station_id, field):
    model = StationMetadataViewSet.get_model_from_table(station_id)
    if field not in [f.name for f in model._meta.fields]:  #mitigating SQL injection risks because custom expression with actual SQL is used
        raise ValidationError('error: Invalid field')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    data = model.calculate_percentiles(field)

    results = list(data)
    if is_ajax:  #if request is ajax it means data will used to render chart, therefore reformatting is needed
        results = prepare_data_for_chart(results)

    return Response(results)

@api_view(['GET'])
def dataseries(request, station_id, field):
    model = StationMetadataViewSet.get_model_from_table(station_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    start_date = escape(request.GET.get('start')) #date from date picker, using django utils to escape (used in custom query)
    end_date = escape(request.GET.get('end') )

    first_non_null_date, last_non_null_date = model.get_date_range(field)

    if (is_ajax) and (start_date != '' and end_date != ''): #request is ajax and date range is specified
        data = model.get_field_data(field, start_date, end_date)
    else:
        data = model.get_field_data(field, first_non_null_date, last_non_null_date)

    min_date = first_non_null_date.strftime('%d-%m-%Y') #format used by date picker in JS
    max_date = last_non_null_date.strftime('%d-%m-%Y')

    response_data = {
        "min_date": min_date,
        "max_date": max_date,
        "data": data
    }

    return Response(response_data)

def site(request):
    return render(request, 'site_template.html')