from django.db import models

# Create your models here.
class Portal(models.Model):
    name = models.CharField(max_length=255, default='unknownPortal')
    url = models.TextField(blank=True)
    token = models.TextField(blank=True)

    class Meta:
        db_table = 'portals'

    def __str__(self):
        return self.name


class Settings(models.Model):
    botToken = models.TextField(blank=True)

    class Meta:
        db_table = 'settings'
