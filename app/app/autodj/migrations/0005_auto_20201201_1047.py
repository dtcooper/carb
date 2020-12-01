# Generated by Django 3.1.3 on 2020-12-01 18:47

import common.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autodj', '0004_auto_20201201_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audioasset',
            name='file',
            field=models.FileField(blank=True, help_text='You can provide either an uploaded audio file or a URL to an external asset.', max_length=512, upload_to=common.models.audio_asset_file_upload_to, verbose_name='audio file'),
        ),
        migrations.AlterField(
            model_name='rotatorasset',
            name='file',
            field=models.FileField(max_length=512, upload_to=common.models.audio_asset_file_upload_to, verbose_name='audio file'),
        ),
    ]
