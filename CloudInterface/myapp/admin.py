from django.contrib import admin
from .models import UserProfile, Task1, Task2

# Displaying the models in the admin panel in list
class Task1Admin(admin.ModelAdmin):
    list_display = ('id', 'airline', 'count', 'user')  # Columns displayed in the admin list view

class Task2Admin(admin.ModelAdmin):
    list_display = ('id', 'Airline', 'Reason', 'Count', 'user')  # Columns displayed in the admin list view

# Registering the models
admin.site.register(UserProfile)
admin.site.register(Task1, Task1Admin)
admin.site.register(Task2, Task2Admin)