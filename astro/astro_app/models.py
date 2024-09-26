from django.db import models

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.username}'

    class Meta:
        managed = False
        db_table = 'auth_user'

class planet(models.Model):
    planetID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=300)
    img = models.CharField(max_length=50, null=True)
    detImg = models.CharField(max_length=50, null=True)
    detDes = models.TextField()

class cons_period(models.Model):
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

    userID = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, related_name='user_reqs')
    moderID = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, related_name='moderated_reqs')

class mm(models.Model):
    planetID = models.ForeignKey(planet, on_delete=models.DO_NOTHING)
    reqID = models.ForeignKey(cons_period, on_delete=models.DO_NOTHING)
    isNew = models.BooleanField(null=True)

    class Meta:
        unique_together = (('planetID', 'reqID'),)