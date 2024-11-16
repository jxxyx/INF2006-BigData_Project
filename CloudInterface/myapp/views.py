from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from .models import Task1
import json

# Create your views here.

# This is the landing page view
def landing_page(request):
    get_template('landing_page.html')
    return render(request, 'landing_page.html')

from django.shortcuts import render
from .models import Task1

def task1_view(request):
    data = Task1.objects.all()
    labels = [item.airline for item in data]
    values = [item.count for item in data]

    # Pass JSON-encoded data to the template
    context = {
        'labels': json.dumps(labels),  # JSON-encode the labels
        'data': json.dumps(values),   # JSON-encode the values
    }
    return render(request, 'task1.html', context)

def task2(request):
    return render(request, 'task2.html')

def task3(request):
    return render(request, 'task3.html')

def task4(request):
    return render(request, 'task4.html')

def task5(request):
    return render(request, 'task5.html')