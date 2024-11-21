from django.contrib import admin
from .models import UserProfile, Task1, Task2, Task3, Task4, Task5_low, Task5_high

# Displaying the models in the admin panel in list
class Task1Admin(admin.ModelAdmin):
    list_display = ('id', 'airline', 'count', 'user')  # Columns displayed in the admin list view

class Task2Admin(admin.ModelAdmin):
    list_display = ('id', 'Airline', 'Reason', 'Count', 'user')  # Columns displayed in the admin list view

class Task3Admin(admin.ModelAdmin):
    list_display = ('id', 'Country', 'Count', 'user')  # Columns displayed in the admin list view

class Task4Admin(admin.ModelAdmin):
    list_display = ('id', 'Channel', 'Mean_Trust_Score', 'Median_Trust_Score', 'Standard_Deviation', 'Sample_Size', 'Min_Score', 'Max_Score', 'user')  # Columns displayed in the admin list view

class Task5_lowAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'airline_sentiment_gold', 'predicted_sentiment', 'correct', 'user')  # Columns displayed in the admin list view

class Task5_highAdmin(admin.ModelAdmin):
    list_display = ('id', 'Text', 'Actual_Sentiment', 'Predicted_Sentiment', 'Correct', 'user')  # Columns displayed in the admin list view

# Registering the models
admin.site.register(UserProfile)
admin.site.register(Task1, Task1Admin)
admin.site.register(Task2, Task2Admin)
admin.site.register(Task3, Task3Admin)
admin.site.register(Task4, Task4Admin)
admin.site.register(Task5_low, Task5_lowAdmin)
admin.site.register(Task5_high, Task5_highAdmin)