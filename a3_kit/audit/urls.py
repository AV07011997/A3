from django.urls import path
from . import views as audit_views


urlpatterns = [
    path('', audit_views.audit_report_page, name="audit_report"),
    path('entitywise/', audit_views.audit_entity, name="audit_entity"),
]
