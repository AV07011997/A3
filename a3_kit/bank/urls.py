from django.urls import path
from . import views as bank_views


urlpatterns = [
    # path('', bank_views.home, name="bank_home"),
    path('processing/', bank_views.home, name="bank_statement_processing"),
]
