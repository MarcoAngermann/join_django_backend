# Generated by Django 5.1.3 on 2024-12-23 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth_app', '0004_alter_customuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_guest',
            field=models.BooleanField(default=False),
        ),
    ]