from django.urls import path
from . import views as test_views

urlpatterns = [
    
    path('', test_views.test, name="test"),
]