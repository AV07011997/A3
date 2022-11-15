from django.urls import path
from . import views as analyze_views


urlpatterns = [
    path('', analyze_views.analyze_page, name="analyze"),
    path('loan_kpi/', analyze_views.loan_kpi, name="loan_kpi"),
    # path('entity_kpi/', analyze_views.entity_kpi, name="entity_kpi"),
    # path('get_analyze_data/', analyze_views.get_analyze_data, name="get_analyze_data"),
    path('bank_customer_month_kpi/', analyze_views.bank_customer_month_kpi, name="bank_customer_month_kpi"),
    path('bank_customer_kpi/', analyze_views.bank_customer_kpi, name="bank_customer_kpi"),
    path('bank_customer_kpi/<type>/<amount>/<accno>', analyze_views.bck_popup, name="bck_popup"),
    path('bank_entity_kpi/', analyze_views.bank_entity_kpi, name="bank_entity_kpi"),
    path('bureauAnalyze/', analyze_views.bureauAnalyze, name="bureauAnalyze"),
    path('bankAnalyze1/', analyze_views.bankAnalyze, name="bankAnalyze"),
    #path('bank_entity_kpi/<entity>/<accno>/', analyze_views.bank_entity, name="bank_entity"),
    path('bank_entity_kpi/entitywise/', analyze_views.bank_entity, name="bank_entity"),
    path('bank_customer_month_kpi/<date>/<maxcredit>/<accno>/', analyze_views.maxcredit, name="maxcredit"),
    path('bureau_customer_kpi/', analyze_views.bureau_customer_kpi, name="bureau_customer_kpi"),
    path('bureau_customer_month_kpi/', analyze_views.bureau_customer_month_kpi, name="bureau_customer_month_kpi"),
    path('itr/', analyze_views.itr, name="itr"),
    path('fishy/', analyze_views.fishy, name="fishy"),
    path('statement/', analyze_views.statement, name="statement"),
    path('statement/lead/', analyze_views.lead, name="lead"),
    path('statement/lead/statement1', analyze_views.statement1, name="statement1"),
    path('bureau_customer_kpi/<cust_id>/',analyze_views.alladress,name="alladress"),
    path('bureau_customer_kpi/age/<cust_id>/',analyze_views.age,name="age"),

]
