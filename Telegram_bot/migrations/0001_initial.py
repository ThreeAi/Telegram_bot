# Generated by Django 4.2 on 2023-05-07 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_tg', models.CharField(max_length=255)),
                ('id_moodle', models.CharField(max_length=255)),
            ],
        ),
    ]
