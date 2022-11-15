from django.urls import path
from . import views as form26as_views


urlpatterns = [
    # path('', form26as_views.home, name="form26as_home"),
    path('processing/', form26as_views.home, name="form26as_processing"),

]