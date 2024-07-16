from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StationMetadataViewSet, yearly_chart_data, ValuesMetadataViewSet, site, get_percentiles, dataseries

router = DefaultRouter()
router.register(r'stations', StationMetadataViewSet)
router.register(r'values', ValuesMetadataViewSet)

urlpatterns = [
    path('', site, name='site'),
    path('api/', include(router.urls)),
    path('api/stations/<str:station_id>/<str:field>/<str:year>/yearly-data/', yearly_chart_data, name='chart-data'),
    path('api/stations/<str:station_id>/<str:field>/percentiles/', get_percentiles, name='get_percentiles'),
    path('api/stations/<str:station_id>/<str:field>/dataseries/', dataseries, name='get_dataseries'),
]