from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('task1/', views.task1_view, name='task1'),
    path('task2/', views.task2_view, name='task2'),
    path('task3/', views.task3_view, name='task3'),
    path('task4/', views.task4_view, name='task4'),
    path('task5/', views.task5, name='task5'),
]
