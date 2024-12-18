# Generated by Django 5.1.4 on 2024-12-16 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0013_customuser_profile_pic_staffs_profile_pic'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sessionyearmodel',
            options={'ordering': ['-session_start_year']},
        ),
        migrations.AlterField(
            model_name='adminhod',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='attendancereport',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='courses',
            name='course_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='courses',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
        migrations.AlterField(
            model_name='feedbackstaffs',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='feedbackstudent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='leavereportstaff',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='leavereportstudent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='notificationstaffs',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='notificationstudent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='staffs',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='staffs',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='staff_profiles/'),
        ),
        migrations.AlterField(
            model_name='staffs',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='studentresult',
            name='updated_at',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='students',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='students',
            name='profile_pic',
            field=models.FileField(blank=True, null=True, upload_to='student_profiles/'),
        ),
        migrations.AlterField(
            model_name='students',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='subjects',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('subject_id', 'attendance_date', 'session_year_id')},
        ),
        migrations.AlterUniqueTogether(
            name='attendancereport',
            unique_together={('student_id', 'attendance_id')},
        ),
        migrations.AlterUniqueTogether(
            name='studentresult',
            unique_together={('student_id', 'subject_id')},
        ),
        migrations.AlterUniqueTogether(
            name='subjects',
            unique_together={('subject_name', 'course_id')},
        ),
    ]
