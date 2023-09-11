from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class QuerySavedModel(models.Model):
    query = models.CharField(max_length=400)
    source = models.CharField(max_length=20)
    last_result = models.CharField(max_length=50)
    updated_on = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, through="UserQueryModel")

class UserQueryModel(models.Model):
    query = models.ForeignKey(QuerySavedModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_result_seen = models.CharField(max_length=50)
    # consulted = models.BooleanField(default=True)
    notified = models.BooleanField(default=False)