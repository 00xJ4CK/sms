# Generated by Django 5.1.4 on 2024-12-15 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0006_alter_session_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default=1, max_length=1),
        ),
    ]