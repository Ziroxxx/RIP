from django.db import models
from django.contrib.auth import get_user_model

class app_planet(models.Model):
    planetID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=300)
    img = models.CharField(max_length=50)
    detImg = models.CharField(max_length=50)
    detDes = models.TextField()

class app_cons_period(models.Model):
    reqID = models.AutoField(primary_key=True)
    dateCreate = models.DateField(auto_now_add=True)
    dateSave = models.DateField(null=True)
    dateFinish = models.DateField(null=True)
    isDraft = models.BooleanField(default=True)
    isSaved = models.BooleanField(default=False)
    isAccepted = models.BooleanField(null=True)
    isCanceled = models.BooleanField(null=True)
    isDeleted = models.BooleanField(default=False)
    dateStart = models.DateField(null=True)
    dateEnd = models.DateField(null=True)
    constellation = models.TextField(max_length=50, null=True)

    userID = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, related_name='user_reqs')
    moderID = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, related_name='moderated_reqs')

class app_mm(models.Model):
    planetID = models.ForeignKey(app_planet, on_delete=models.DO_NOTHING)
    reqID = models.ForeignKey(app_cons_period, on_delete=models.DO_NOTHING)
    isNew = models.BooleanField(null=True)

    class Meta:
        unique_together = (('planetID', 'reqID'),)