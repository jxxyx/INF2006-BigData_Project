from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('task1/', views.task1, name='task1'),
    path('task2/', views.task2, name='task2'),
    path('task2/', views.task3, name='task3'),
    path('task2/', views.task4, name='task4'),
    path('task2/', views.task5, name='task5')
]