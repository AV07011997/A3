from django.urls import path
from . import views as salary_views


urlpatterns = [
    path('', salary_views.upload_salary_page, name="upload_salary"),
]
