from django.db import models

class Users(models.Model):
    id_tg = models.CharField(max_length=255)
    id_moodle = models.CharField(max_length=255)
