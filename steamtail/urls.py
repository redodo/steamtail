from django.urls import path

from . import views

urlpatterns = [
    path('app/<pk>/', views.AppDetail.as_view(), name='app_detail'),
    path('app/<pk>/info/', views.AppInfo.as_view(), name='app_info'),
    path('app/<pk>/info/<other>/', views.AppInfo.as_view(), name='app_info_other'),
    path('sim/<pk_a>/<pk_b>/', views.app_similarity),
    path('sim/<pk_a>/', views.apps_like_this, name='more_like_this'),
    path('concept/', views.AppConcept.as_view(), name='app_concept'),
]
