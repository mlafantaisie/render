from django.contrib import admin
from django.urls import path
from . import views
from .views import upload_data
from .views import data_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
]
