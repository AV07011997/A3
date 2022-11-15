from django.urls import path
from . import views as form16_views


urlpatterns = [
    # path('', form16_views.home, name="form16_home"),
    path('processing/', form16_views.home, name="form16_processing"),
]
