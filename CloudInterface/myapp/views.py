from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template

# Create your views here.

# This is the landing page view
def landing_page(request):
    get_template('landing_page.html')
    return render(request, 'landing_page.html')

def test_page(request):
    return HttpResponse("<h1>Test Page</h1>")