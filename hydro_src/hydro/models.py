from django.contrib.gis.db import models
from django.db.models import F, Func, Max, Min
from .aggregates import Percentile

class BaseStationModel(models.Model): #base station class inherited by all station models
    class Meta:
        abstract = True

    @classmethod
    def get_date_range(cls, field): #parameters within station dont have the same date range of measurements
        first_non_null_date = cls.objects.filter(**{f"{field}__isnull": False}).aggregate(min_date=Min('date_time'))['min_date']
        last_non_null_date = cls.objects.filter(**{f"{field}__isnull": False}).aggregate(max_date=Max('date_time'))['max_date']
        return first_non_null_date, last_non_null_date

    @classmethod
    def get_field_data(cls, field, start_date, end_date):
        data = cls.objects.filter(date_time__gte=start_date, date_time__lte=end_date).annotate(
            date=F('date_time'),
            value=F(field)
            ).values('date', 'value').order_by('date')
        return data
    
    @classmethod
    def calculate_percentiles(cls, field): #aggregating by month and ignoring year, used for yearly chart
        queryset = (cls.objects.annotate(string_date_without_year=Func(
                            F('date_time'), function='to_char', template="%(function)s(date_trunc('month', %(expressions)s), 'MM-DD\"T\"HH24:MI:SS')"))
                        .values('string_date_without_year')
                        .annotate(
                            q10=Percentile(0.10, F(field)),
                            q20=Percentile(0.20, F(field)),
                            q30=Percentile(0.30, F(field)),
                            q40=Percentile(0.40, F(field)),
                            q50=Percentile(0.50, F(field)),
                            q60=Percentile(0.60, F(field)),
                            q70=Percentile(0.70, F(field)),
                            q80=Percentile(0.80, F(field)),
                            q90=Percentile(0.90, F(field)))
                        .order_by('string_date_without_year'))

        return queryset

class AntyglPritok(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)
    wt_wl_degc = models.FloatField(db_column='WT_WL_degC', blank=True, null=True) 
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'antygl_pritok'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BreznickyPotok(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    gr_w_m2 = models.FloatField(db_column='GR_W/m2', blank=True, null=True)   
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    ws_m_s = models.FloatField(db_column='WS_m/s', blank=True, null=True)   
    wd_deg = models.FloatField(db_column='WD_deg', blank=True, null=True)  
    rx_mv = models.FloatField(db_column='RX_mV', blank=True, null=True)  
    wt_rx_degc = models.FloatField(db_column='WT_RX_degC', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    wt_ec_degc = models.FloatField(db_column='WT_EC_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'breznicky_potok'


class CernyPotok(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    rx_mv = models.FloatField(db_column='RX_mV', blank=True, null=True)  
    wt_red_degc = models.FloatField(db_column='WT_red_degC', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    wt_ph_degc = models.FloatField(db_column='WT_pH_degC', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'cerny_potok'


class CikanskyPotok(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    wt_ec_degc = models.FloatField(db_column='WT_EC_degC', blank=True, null=True)  
    wt_ph_degc = models.FloatField(db_column='WT_pH_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'cikansky_potok'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Filipohutsky(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    wt_ec_degc = models.FloatField(db_column='WT_EC_degC', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'filipohutsky'


class HrabeciCesta(BaseStationModel):
    at20_degc = models.FloatField(db_column='AT20_degC', blank=True, null=True)  
    rh20_pct = models.FloatField(db_column='RH20_pct', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    ws_m_s = models.FloatField(db_column='WS_m/s', blank=True, null=True)   
    hs_cm = models.FloatField(db_column='HS_cm', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    ws_2_m_s = models.FloatField(db_column='WS_2_m/s', blank=True, null=True)   
    sm10_pct = models.FloatField(db_column='SM10_pct', blank=True, null=True)  
    st10_degc = models.FloatField(db_column='ST10_degC', blank=True, null=True)  
    sm25_pct = models.FloatField(db_column='SM25_pct', blank=True, null=True)  
    st25_degc = models.FloatField(db_column='ST25_degC', blank=True, null=True)  
    sm60_pct = models.FloatField(db_column='SM60_pct', blank=True, null=True)  
    st60_degc = models.FloatField(db_column='ST60_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'hrabeci_cesta'


class HrebecnaMeteo(BaseStationModel):
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    hs_mm = models.FloatField(db_column='HS_mm', blank=True, null=True)  
    gr_w_m2 = models.FloatField(db_column='GR_W/m2', blank=True, null=True)   
    ws_m_s = models.FloatField(db_column='WS_m/s', blank=True, null=True)   
    wd_deg = models.FloatField(db_column='WD_deg', blank=True, null=True)  
    gt05_degc = models.FloatField(db_column='GT05_degC', blank=True, null=True)  
    at50_degc = models.FloatField(db_column='AT50_degC', blank=True, null=True)  
    at20_degc = models.FloatField(db_column='AT20_degC', blank=True, null=True)  
    sm_neg60_pct = models.FloatField(db_column='SM60_pct', blank=True, null=True)  
    sm30_pct = models.FloatField(db_column='SM30_pct', blank=True, null=True)  
    sm15_pct = models.FloatField(db_column='SM15_pct', blank=True, null=True)  
    st_neg60_degc = models.FloatField(db_column='ST60_degC', blank=True, null=True)  
    st30_degc = models.FloatField(db_column='ST30_degC', blank=True, null=True)  
    st15_degc = models.FloatField(db_column='ST15_degC', blank=True, null=True)  
    at25_degc = models.FloatField(db_column='AT25_degC', blank=True, null=True)  
    at75_degc = models.FloatField(db_column='AT75_degC', blank=True, null=True)  
    at100_degc = models.FloatField(db_column='AT100_degC', blank=True, null=True)  
    grout_w_m2 = models.FloatField(db_column='GRout_W/m2', blank=True, null=True)   
    ws_2_m_s = models.FloatField(db_column='WS_2_m/s', blank=True, null=True)   
    wd_2_deg = models.FloatField(db_column='WD_2_deg', blank=True, null=True)  
    wsmax_m_s = models.FloatField(db_column='WSmax_m/s', blank=True, null=True)   
    wsmin_m_s = models.FloatField(db_column='WSmin_m/s', blank=True, null=True)   
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'hrebecna_meteo'


class Javori(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    q_m3_s = models.FloatField(db_column='Q_m3/s', blank=True, null=True)   
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    sm_41_pct = models.FloatField(db_column='SM_41_pct', blank=True, null=True)  
    st_42_degc = models.FloatField(db_column='ST_42_degC', blank=True, null=True)  
    sm_43_pct = models.FloatField(db_column='SM_43_pct', blank=True, null=True)  
    st_44_degc = models.FloatField(db_column='ST_44_degC', blank=True, null=True)  
    sm_45_pct = models.FloatField(db_column='SM_45_pct', blank=True, null=True)  
    st_46_degc = models.FloatField(db_column='ST_46_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'javori'


class JavoriPila(BaseStationModel):
    hs_cm = models.FloatField(db_column='HS_cm', blank=True, null=True)  
    swe_mm = models.BigIntegerField(db_column='SWE_mm', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    hs_laser_cm = models.FloatField(db_column='HS_laser_cm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'javori_pila'


class Kremelna(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'kremelna'


class LoseniceRejstejn(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'losenice_rejstejn'


class ModravaMeteoH7(BaseStationModel):
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    hs_cm = models.FloatField(db_column='HS_cm', blank=True, null=True)  
    gr_w_m2 = models.FloatField(db_column='GR_W/m2', blank=True, null=True)   
    grout_w_m2 = models.FloatField(db_column='GRout_W/m2', blank=True, null=True)   
    swe_mm = models.FloatField(db_column='SWE_mm', blank=True, null=True)  
    ws_m_s = models.FloatField(db_column='WS_m/s', blank=True, null=True)   
    wd_deg = models.FloatField(db_column='WD_deg', blank=True, null=True)  
    ws_2_m_s = models.FloatField(db_column='WS_2_m/s', blank=True, null=True)   
    wd_2_deg = models.FloatField(db_column='WD_2_deg', blank=True, null=True)  
    wsmax_m_s = models.FloatField(db_column='WSmax_m/s', blank=True, null=True)   
    wsmin_m_s = models.FloatField(db_column='WSmin_m/s', blank=True, null=True)   
    rh_2_pct = models.FloatField(db_column='RH_2_pct', blank=True, null=True)  
    at_2_degc = models.FloatField(db_column='AT_2_degC', blank=True, null=True)  
    atmin_2_degc = models.FloatField(db_column='ATmin_2_degC', blank=True, null=True)  
    atmax_2_degc = models.FloatField(db_column='ATmax_2_degC', blank=True, null=True)  
    sm10_pct = models.FloatField(db_column='SM10_pct', blank=True, null=True)  
    st10_degc = models.FloatField(db_column='ST10_degC', blank=True, null=True)  
    sm25_pct = models.FloatField(db_column='SM25_pct', blank=True, null=True)  
    st25_degc = models.FloatField(db_column='ST25_degC', blank=True, null=True)  
    sm60_pct = models.FloatField(db_column='SM60_pct', blank=True, null=True)  
    st60_degc = models.FloatField(db_column='ST60_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'modrava_meteo_h7'


class Modravsky(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    wt_ec_degc = models.FloatField(db_column='WT_EC_degC', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'modravsky'


class Netradio1(BaseStationModel):
    gr_w_m2 = models.FloatField(db_column='GR_W/m2', blank=True, null=True)   
    grout_w_m2 = models.FloatField(db_column='GRout_W/m2', blank=True, null=True)   
    lwin_w_m2 = models.FloatField(db_column='LWin_W/m2', blank=True, null=True)   
    lwout_w_m2 = models.FloatField(db_column='LWout_W/m2', blank=True, null=True)   
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'netradio_1'


class Netradio2(BaseStationModel):
    gr_w_m2 = models.FloatField(db_column='GR_W/m2', blank=True, null=True)   
    grout_w_m2 = models.FloatField(db_column='GRout_W/m2', blank=True, null=True)   
    lwin_w_m2 = models.FloatField(db_column='LWin_W/m2', blank=True, null=True)   
    lwout_w_m2 = models.FloatField(db_column='LWout_W/m2', blank=True, null=True)   
    hs_mm = models.FloatField(db_column='HS_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'netradio_2'


class Netradio3(BaseStationModel):
    gr_w_m2 = models.FloatField(db_column='GR_W/m2', blank=True, null=True)   
    grout_w_m2 = models.FloatField(db_column='GRout_W/m2', blank=True, null=True)   
    lwin_w_m2 = models.FloatField(db_column='LWin_W/m2', blank=True, null=True)   
    lwout_w_m2 = models.FloatField(db_column='LWout_W/m2', blank=True, null=True)   
    hs_mm = models.FloatField(db_column='HS_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'netradio_3'


class PrasilskyPot(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'prasilsky_pot'


class Ptaci(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    q_m3_s = models.FloatField(db_column='Q_m3/s', blank=True, null=True)   
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    hs_cm = models.FloatField(db_column='HS_cm', blank=True, null=True)  
    st_neg10_degc = models.FloatField(db_column='ST10_degC', blank=True, null=True)  
    gt05_degc = models.FloatField(db_column='GT05_degC', blank=True, null=True)  
    at40_degc = models.FloatField(db_column='AT40_degC', blank=True, null=True)  
    at80_degc = models.FloatField(db_column='AT80_degC', blank=True, null=True)  
    at120_degc = models.FloatField(db_column='AT120_degC', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    wl_2_mm = models.FloatField(db_column='WL_2_mm', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    wt_ph_degc = models.FloatField(db_column='WT_pH_degC', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'ptaci'


class PtaciSpa(BaseStationModel):
    hs_cm = models.BigIntegerField(db_column='HS_cm', blank=True, null=True)  
    at120_degc = models.FloatField(db_column='AT120_degC', blank=True, null=True)  
    at90_degc = models.FloatField(db_column='AT90_degC', blank=True, null=True)  
    at60_degc = models.FloatField(db_column='AT60_degC', blank=True, null=True)  
    at30_degc = models.FloatField(db_column='AT30_degC', blank=True, null=True)  
    gt05_degc = models.FloatField(db_column='GT05_degC', blank=True, null=True)  
    st10_degc = models.FloatField(db_column='ST10_degC', blank=True, null=True)  
    swe_mm = models.FloatField(db_column='SWE_mm', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'ptaci_spa'


class PtaiPotokIsco(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'ptaci_potok_isco'


class RanklovskyPotok(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    wt_ph_degc = models.FloatField(db_column='WT_pH_degC', blank=True, null=True)  
    do_mg_l = models.FloatField(db_column='DO_mg/l', blank=True, null=True)   
    wt_do_degc = models.FloatField(db_column='WT_DO_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'ranklovsky_potok'

class RoklanskyHajenka(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'roklansky_hajenka'

class RoklanskyPot(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    q_m3_s = models.FloatField(db_column='Q_m3/s', blank=True, null=True)   
    ec_3_micros_cm = models.FloatField(db_column='EC_3_microS/cm', blank=True, null=True)   
    ec_4_micros_cm = models.FloatField(db_column='EC_4_microS/cm', blank=True, null=True)   
    ec_5_micros_cm = models.FloatField(db_column='EC_5_microS/cm', blank=True, null=True)   
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'roklansky_pot'


class Rokytka(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    q_m3_s = models.FloatField(db_column='Q_m3/s', blank=True, null=True)   
    hs_cm = models.FloatField(db_column='HS_cm', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    swe_mm = models.FloatField(db_column='SWE_mm', blank=True, null=True)  
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    wt_ph_degc = models.FloatField(db_column='WT_pH_degC', blank=True, null=True)  
    rx_mv = models.FloatField(db_column='RX_mV', blank=True, null=True)  
    wt_ecdegc = models.FloatField(db_column='WT_ECdegC', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    ws_m_s = models.FloatField(db_column='WS_m/s', blank=True, null=True)   
    wd_deg = models.FloatField(db_column='WD_deg', blank=True, null=True)  
    ws_2_m_s = models.FloatField(db_column='WS_2_m/s', blank=True, null=True)   
    wd_2_deg = models.FloatField(db_column='WD_2_deg', blank=True, null=True)  
    wsmax_m_s = models.FloatField(db_column='WSmax_m/s', blank=True, null=True)   
    wsmin_m_s = models.FloatField(db_column='WSmin_m/s', blank=True, null=True)   
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'rokytka'


class SebestianMeteo(BaseStationModel):
    ws_m_s = models.FloatField(db_column='WS_m/s', blank=True, null=True)   
    wd_deg = models.FloatField(db_column='WD_deg', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    gr_w_m2 = models.FloatField(db_column='GR_W/m2', blank=True, null=True)   
    st10_degc = models.FloatField(db_column='ST10_degC', blank=True, null=True)  
    gt05_degc = models.FloatField(db_column='GT05_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'sebestian_meteo'


class SlatinnyKh(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    wl_2_mm = models.FloatField(db_column='WL_2_mm', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    ec_uncomp_micros_cm = models.FloatField(db_column='EC_uncomp_microS/cm', blank=True, null=True)   
    ph = models.FloatField(db_column='pH_-', blank=True, null=True)    
    wt_ph_degc = models.FloatField(db_column='WT_pH_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'slatinny_kh'


class SlatinnyPotok(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'slatinny_potok'


class StationMetadata(models.Model):
    st_name = models.TextField(blank=True, primary_key=True) 
    st_label = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    masl_m_field = models.BigIntegerField(db_column='masl (m)', blank=True, null=True) 
    geom = models.PointField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'station_metadata'


class Tmavy(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    ec_lin_micros_cm = models.FloatField(db_column='EC_lin_microS/cm', blank=True, null=True)   
    ec_nonlin_micros_cm = models.FloatField(db_column='EC_nonlin_microS/cm', blank=True, null=True)   
    wt_ec_degc = models.FloatField(db_column='WT_EC_degC', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'tmavy'


class ValuesMetadata(models.Model):
    parameter = models.TextField(db_column='Parameter')  
    parameter_abreviation_in_data_file = models.TextField(db_column='Parameter abreviation in data file')   
    unit = models.TextField(db_column='Unit')  
    django_field_name = models.TextField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'values_metadata'
        unique_together = (('parameter', 'parameter_abreviation_in_data_file'),)


class VolynkaMalenice(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'volynka_malenice'


class VolynkaVimperk(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'volynka_vimperk'


class ZhureckyPot(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'zhurecky_pot'


class ZlatyHubertky(BaseStationModel):
    swe_1_mm = models.FloatField(db_column='SWE_1_mm', blank=True, null=True)  
    swe_mm = models.FloatField(db_column='SWE_mm', blank=True, null=True)  
    hs_mm = models.FloatField(db_column='HS_mm', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    hs_2_mm = models.FloatField(db_column='HS_2_mm', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'zlaty_hubertky'


class ZlatyMeteoHlad(BaseStationModel):
    wl_mm = models.FloatField(db_column='WL_mm', blank=True, null=True)  
    p_mm = models.FloatField(db_column='P_mm', blank=True, null=True)  
    hs_cm = models.FloatField(db_column='HS_cm', blank=True, null=True)  
    at_degc = models.FloatField(db_column='AT_degC', blank=True, null=True)  
    rh_pct = models.FloatField(db_column='RH_pct', blank=True, null=True)  
    wt_degc = models.FloatField(db_column='WT_degC', blank=True, null=True)  
    date_time = models.DateTimeField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'zlaty_meteo_hlad'
