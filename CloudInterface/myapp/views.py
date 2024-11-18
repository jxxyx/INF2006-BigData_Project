from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from .models import Task1, Task2, Task3, Task4
import json
from collections import defaultdict

# Create your views here.

# This is the landing page view
def landing_page(request):
    get_template('landing_page.html')
    return render(request, 'landing_page.html')

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

def task2_view(request):
    task2_data = Task2.objects.all()
    airline_data = defaultdict(lambda: {"labels": [], "data": []})

    # Group data by airline
    for entry in task2_data:
        airline_data[entry.Airline]["labels"].append(entry.Reason)
        airline_data[entry.Airline]["data"].append(entry.Count)

    # Pass JSON-encoded data for all airlines to the template
    context = {
        'airline_data': json.dumps(airline_data),  # JSON-encode the grouped data
    }
    return render(request, 'task2.html', context)

def task3_view(request):
    task3_data = Task3.objects.all()
    labels = [entry.Country for entry in task3_data]
    data = [entry.Count for entry in task3_data]
    
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }
    return render(request, 'task3.html', context)

def task4_view(request):
    task4_data = Task4.objects.all()
    labels = [entry.Channel for entry in task4_data]
    data = [{
        'min': float(entry.Min_Score),
        'q1': float(entry.Mean_Trust_Score) - float(entry.Standard_Deviation),
        'median': float(entry.Median_Trust_Score),
        'q3': float(entry.Mean_Trust_Score) + float(entry.Standard_Deviation),
        'max': float(entry.Max_Score)
    } for entry in task4_data]
    
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }
    return render(request, 'task4.html', context)

def task5(request):
    return render(request, 'task5.html')