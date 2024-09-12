from django.db import models
from django.contrib.auth import get_user_model

class planets(models.Model):
    planetID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=300)
    img = models.CharField(max_length=50)
    detImg = models.CharField(max_length=50)
    detDes = models.TextField()
    constellations = models.TextField(null=True)
    transfer_dates = models.TextField(null=True)

class requests(models.Model):
    reqID = models.AutoField(primary_key=True)
    dateCreate = models.DateField(auto_now_add=True)
    dateFinished = models.DateField(null=True)
    isDraft = models.BooleanField(default=True)
    isSaved = models.BooleanField(default=False)
    isAccepted = models.BooleanField(default=False)
    isCanceled = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)

    userID = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='user_reqs')
    moderID = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name='moderated_reqs')

class mm(models.Model):
    planetID = models.ForeignKey(planets, on_delete=models.CASCADE)
    reqID = models.ForeignKey(requests, on_delete=models.CASCADE)
    curConstellation = models.TextField()

    class Meta:
        unique_together = (('planetID', 'reqID'),)