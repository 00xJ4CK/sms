from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    object = models.Manager()  # Keeping original naming

    class Meta:
        ordering = ["-session_start_year"]

    def clean(self):
        if self.session_end_year <= self.session_start_year:
            raise ValidationError("End year must be after start year")

    def __str__(self):
        return f"{self.session_start_year} to {self.session_end_year}"


# Keeping Session model since it was in original code
class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()
    object = models.Manager()  # Keeping original naming

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    user_type_data = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    user_type = models.CharField(
        default=1,
        choices=user_type_data,
        max_length=10,
    )


class AdminHOD(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    fcm_token = models.TextField(default="")
    objects = models.Manager()


class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class Subjects(models.Model):
    id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    course_id = models.ForeignKey(
        Courses, on_delete=models.CASCADE, default=1
    )  # Kept original name
    staff_id = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE
    )  # Kept original name
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()

    class Meta:
        unique_together = ["subject_name", "course_id"]


class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=255)
    profile_pic = models.FileField(upload_to="student_profiles/", null=True, blank=True)
    address = models.TextField(blank=True)
    course_id = models.ForeignKey(
        Courses, on_delete=models.DO_NOTHING
    )  # Kept original name and on_delete
    session_year_id = models.ForeignKey(
        SessionYearModel, on_delete=models.CASCADE
    )  # Kept original name
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    fcm_token = models.TextField(default="")
    objects = models.Manager()


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(
        Subjects, on_delete=models.DO_NOTHING
    )  # Kept original name
    attendance_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    session_year_id = models.ForeignKey(
        SessionYearModel, on_delete=models.CASCADE
    )  # Kept original name
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()

    class Meta:
        unique_together = ["subject_id", "attendance_date", "session_year_id"]


class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(
        Students, on_delete=models.DO_NOTHING
    )  # Kept original name
    attendance_id = models.ForeignKey(
        Attendance, on_delete=models.CASCADE
    )  # Kept original name
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()

    class Meta:
        unique_together = ["student_id", "attendance_id"]


class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(
        Students, on_delete=models.CASCADE
    )  # Kept original name
    leave_date = models.CharField(max_length=255)  # Kept as CharField
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)  # Kept original name
    leave_date = models.CharField(max_length=255)  # Kept as CharField
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(
        Students, on_delete=models.CASCADE
    )  # Kept original name
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)  # Kept original name
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(
        Students, on_delete=models.CASCADE
    )  # Kept original name
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)  # Kept original name
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()


class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(
        Students, on_delete=models.CASCADE
    )  # Kept original name
    subject_id = models.ForeignKey(
        Subjects, on_delete=models.CASCADE
    )  # Kept original name
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)  # Changed from auto_now_add
    objects = models.Manager()

    class Meta:
        unique_together = ["student_id", "subject_id"]


class OnlineClassRoom(models.Model):
    id = models.AutoField(primary_key=True)
    room_name = models.CharField(max_length=255)
    room_pwd = models.CharField(max_length=255)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    session_years = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    started_by = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.user_type == 1:
        AdminHOD.objects.create(admin=instance)
    elif instance.user_type == 2:
        Staffs.objects.create(admin=instance, address="")
    elif instance.user_type == 3:
        Students.objects.create(
            admin=instance,
            course_id=Courses.objects.get(id=1),
            session_year_id=SessionYearModel.object.get(id=1),
            address="",
            profile_pic="",
            gender="",
        )


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    elif instance.user_type == 2:
        instance.staffs.save()
    elif instance.user_type == 3:
        instance.students.save()
