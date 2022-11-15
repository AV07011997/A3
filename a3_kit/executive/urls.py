from django.urls import path, include
from . import views as executive_views
from django.contrib.auth import views as auth_views


urlpatterns = [


  path('', executive_views.executive_summary, name="executive_summary"),
  path('/savedata/', executive_views.savedata, name="savedata"),
  
  
]
