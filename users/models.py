from django.db import models

class History(models.Model):
    uid = models.IntegerField()
    question = models.TextField() 
    answer = models.TextField()
    marks = models.TextField()

