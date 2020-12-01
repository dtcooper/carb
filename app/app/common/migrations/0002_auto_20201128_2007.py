# Generated by Django 3.1.3 on 2020-11-29 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(help_text='This is needed to match Google Calendar events for calendar based harbor authorization.', max_length=254, unique=True, verbose_name='email address'),
        ),
    ]