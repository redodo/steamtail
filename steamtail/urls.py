from django.urls import path

from . import views

urlpatterns = [
    path('app/<pk>/', views.AppDetail.as_view(), name='app_detail'),
]
