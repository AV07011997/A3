from django.urls import path
from . import views as itrv_views


urlpatterns = [
    # path('', itrv_views.home, name="itrv_home"),
    path('processing/', itrv_views.home, name="itrv_processing"),

]
