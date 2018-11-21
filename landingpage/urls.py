from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<str:profile_name>', views.profile, name='profile'),
    path('profile/<str:profile_name>/download', views.download_profile, name='download_profile'),
    path('profile/<str:profile_name>/analyze', views.analyze_profile, name='analyze_profile'),
    path('recommendations/<str:profile_name>', views.recommendations, name='recommendations'),
    path('recommendations/<str:profile_name>/upload', views.upload_candidates, name='upload_candidates'),
    path('recommendations/<str:profile_name>/analyze', views.analyze_candidates, name='analyze_candidates'),
]