from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.SearchPage, name='search_result'),
    path('chart/', views.DisplayChart, name='display_chart'),
    path('reviewanalysis/', views.reviewAnalysis, name='review_analysis'),
]