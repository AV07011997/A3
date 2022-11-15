from django.urls import path
from . import views as pan_views


urlpatterns = [
    # path('', pan_views.home, name="pan_home"),
    path('processing/', pan_views.home, name="pan_processing"),

]
