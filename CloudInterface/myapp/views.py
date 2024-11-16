from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template

# Create your views here.

# This is the landing page view
def landing_page(request):
    get_template('landing_page.html')
    return render(request, 'landing_page.html')

def task1(request):
    return render(request, 'task1.html')

def task2(request):
    return render(request, 'task2.html')

def task3(request):
    return render(request, 'task3.html')

def task4(request):
    return render(request, 'task4.html')

def task5(request):
    return render(request, 'task5.html')