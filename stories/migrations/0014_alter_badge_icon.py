# Generated by Django 5.1.1 on 2024-09-29 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0013_alter_badge_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to='badges/'),
        ),
    ]
