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
    
class Task2(models.Model):
    Airline = models.CharField(max_length=50)
    Reason = models.CharField(max_length=2000)
    Count = models.IntegerField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.Airline
    
class Task4(models.Model):
    Channel = models.CharField(max_length=50)
    Mean_Trust_Score = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    Median_Trust_Score = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    Standard_Deviation = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    Sample_Size = models.IntegerField(default=0)
    Min_Score = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    Max_Score = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.Channel
    
class Task5_low(models.Model):
    text = models.CharField(max_length=2000)
    airline_sentiment_gold = models.CharField(max_length=50)
    predicted_sentiment = models.CharField(max_length=50)
    correct = models.IntegerField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.Text
    
class Task5_high(models.Model):
    text = models.CharField(max_length=2000)
    airline_sentiment_gold = models.CharField(max_length=50)
    predicted_sentiment = models.CharField(max_length=50)
    correct = models.IntegerField(default=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.Text
