from django.urls import path, include
from . import views as mysite_views
from django.contrib.auth import views as auth_views


urlpatterns = [


    path('', mysite_views.home_page, name="mysite_home"),
    path('login/', mysite_views.login_page, name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('search/', mysite_views.search_page, name="search"),
    path('search/searchsession/<str:text>/', mysite_views.searchsession, name="searchsession"),
    path('search/customer_id1234/', mysite_views.customer_id1234, name="customer_id1234"),
    path('search/customer_id1234/customer_session/<str:text>/<str:text1>/', mysite_views.customer_session, name="customer_session"),
    path('search_result/<str:text>/', mysite_views.search_result, name="search_result"),
    path('doclist/<str:ptype>/', mysite_views.doclist_page, name="doclist"),
    path('delete_doclist_data/<str:xid>/', mysite_views.delete_doclist_data, name="delete_doclist_data"),
    path('loan/<str:deal_id>/', mysite_views.loan_page, name="loan"),
    path('add_user_details/', mysite_views.add_user_details, name="add_user_details"),
    path('set_session/', mysite_views.set_session, name="set_session"),
    path('get_pan_image/', mysite_views.get_pan_image, name="get_pan_image"),
    path('get_aadhaar_image/', mysite_views.get_aadhaar_image, name="get_aadhaar_image"),
    path('remove_pan_image/', mysite_views.remove_pan_image, name="remove_pan_image"),
    path('remove_aadhaar_image/', mysite_views.remove_aadhaar_image, name="remove_aadhaar_image"),
    
    path('upload_form/', mysite_views.upload_form_page, name="upload_form"),
    path('get_itrv_form16_form26as_files/', mysite_views.get_itrv_form16_form26as_files, name="get_itrv_form16_form26as_files"),
    path('remove_itrv_image/', mysite_views.remove_itrv_image, name="remove_itrv_image"),
    path('remove_form16_image/', mysite_views.remove_form16_image, name="remove_form16_image"),
    path('remove_form26as_image/', mysite_views.remove_form26as_image, name="remove_form26as_image"),


    path('upload_bank_statement/', mysite_views.upload_bank_statement_page, name="upload_bank_statement"),
    path('get_bank_statement_files/', mysite_views.get_bank_statement_files, name="get_bank_statement_files"),
    path('remove_bank_statements/', mysite_views.remove_bank_statements, name="remove_bank_statements"),

    
    path('upload_salary/', include('salary.urls'), name="upload_salary"),
    path('bureau/', include('bureau.urls'), name="bureau"),
    path('audit_report/', include('audit.urls'), name="audit_report"),
    path('upload/<str:doc_type>/', mysite_views.upload_page, name="upload"),
    path('table/', mysite_views.table_page, name="table"),
    path('aadhaar/', include('aadhaar.urls')),
    path('pan/', include('pan.urls')),
    path('bank/', include('bank.urls')),
    path('itrv/', include('itrv.urls')),
    path('form26as/', include('form26as.urls')),
    path('form16/', include('form16.urls')),

    path('analyze/', include('analyze.urls')),
    
    path('upload_file/', include('upload_files.urls')),
    path("executive",include('executive.urls'),name="executive"),
]
