# Generated by Django 5.0.7 on 2025-03-20 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0007_alter_feedback_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
