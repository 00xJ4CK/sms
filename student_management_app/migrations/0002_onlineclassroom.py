# Generated by Django 5.1.4 on 2024-12-14 10:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("student_management_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OnlineClassRoom",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("room_name", models.CharField(max_length=255)),
                ("room_pwd", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                (
                    "session_years",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_management_app.SessionYearModel",
                    ),
                ),
                (
                    "started_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_management_app.Staffs",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_management_app.Subjects",
                    ),
                ),
            ],
        ),
    ]
