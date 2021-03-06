# Generated by Django 3.2rc1 on 2021-06-11 21:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autodj', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='weight',
            field=models.FloatField(default=1.0, help_text="The weight (ie selection bias) for how likely random selection from this playlist/stopset occurs, eg '1.0' is just as likely as all others, '2.0' is 2x as likely, '3.0' is 3x as likely, '0.5' half as likely, and so on. If unsure, leave as '1.0'.", validators=[django.core.validators.MinValueValidator(1e-05)], verbose_name='random weight'),
        ),
        migrations.AlterField(
            model_name='stopset',
            name='weight',
            field=models.FloatField(default=1.0, help_text="The weight (ie selection bias) for how likely random selection from this playlist/stopset occurs, eg '1.0' is just as likely as all others, '2.0' is 2x as likely, '3.0' is 3x as likely, '0.5' half as likely, and so on. If unsure, leave as '1.0'.", validators=[django.core.validators.MinValueValidator(1e-05)], verbose_name='random weight'),
        ),
    ]
