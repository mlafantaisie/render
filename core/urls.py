from django.contrib import admin
from django.urls import path
from . import views
from .views import upload_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
]
