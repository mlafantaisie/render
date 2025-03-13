from django.contrib import admin
from django.urls import path
from . import views
from .views import upload_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("upload/", upload_data, name="upload_data"),
]
