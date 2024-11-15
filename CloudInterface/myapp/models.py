# import models from django.db
from django.db import models

# Defining the User class here to store the user details
class UserProfile(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    # returns it as a string in the /admin portion of the website
    def __str__(self):
        return self.username
    
class Task1(models.Model):
    airline = models.CharField(max_length=50)
    count = models.IntegerField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.airline