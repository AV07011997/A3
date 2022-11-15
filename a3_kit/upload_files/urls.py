from django.urls import path
from . import views as upload_file

urlpatterns = [

    path('', upload_file.upload_statments, name="upload_statments"),
    path('search/<str:text>/', upload_file.search_by_lead_name, name="search_by_lead_name"),
    path('get_file_count/',upload_file.get_count_by_lead_id_name,name='get_count_by_lead_id_name'),
    path('bank_statments/',upload_file.uploadBankStatments,name='upload_Bank_Statments'),
    path('ITR_statments/',upload_file.uploadITRStatments,name='upload_ITR_Statments'),
    path('download/',upload_file.download_statments,name="download_statments"),
    path('search/download/<str:text>/', upload_file.search_by_lead_name_for_download, name="search_by_lead_name_for_download"),
   
    path('get_about_leadID/',upload_file.get_about_lead_id,name='get_about_lead_id'),
    path('download_files_by_lead/',upload_file.download_files_by_lead,name='download_files_by_lead'),
    path('update_after_download/',upload_file.update_after_download,name="update_bank_after_download"),
    path('update_cust_id_if_c_gr_0/',upload_file.update_cust_id_if_c_gr_0,name='update_cust_id_if_c_gr_0'),

    


]