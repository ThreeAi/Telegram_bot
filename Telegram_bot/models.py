from django.db import models

class Users(models.Model):
    id_tg = models.CharField(unique=True, max_length=255)
    id_moodle = models.CharField(max_length=255)

class Courses(models.Model):
    id_course = models.IntegerField(unique=True)
    short_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
