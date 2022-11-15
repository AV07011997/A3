from django.urls import path
from . import views as bureau_views


urlpatterns = [
    path('', bureau_views.bureau_page, name="bureau"),
    path('get_bureau_data/', bureau_views.get_bureau_data, name="get_bureau_data"),
    path('update_bureau_data/', bureau_views.update_bureau_data, name="update_bureau_data"),
    path('reset_bureau_data/', bureau_views.reset_bureau_data, name="reset_bureau_data"),
    path('selected_bureau_data/', bureau_views.selected_bureau_data, name="selected_bureau_data"),
    path('final_selected_data/', bureau_views.some, name="final_selected_bureau_data"),
    path('update_bureau_tenure_dpd/',bureau_views.updateBureauAccountSegmentTl,name="update_bureau_account_segment_tl_Tenure and DPD"),
    path('bureau_data_by_condition/', bureau_views.bureau_data_by_condition, name="bureau_data_by_condition"),
]
