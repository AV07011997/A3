from django.urls import path
from . import views as aadhaar_views


urlpatterns = [
    # path('', aadhaar_views.home, name="aadhaar_home"),
    path('processing/', aadhaar_views.home, name="aadhaar_processing"),
]
