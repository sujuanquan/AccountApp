# Generated by Django 5.1.1 on 2024-10-15 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_account01', '0003_remove_account_expand'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='expand',
            field=models.IntegerField(default=0, verbose_name='Expand'),
        ),
    ]
