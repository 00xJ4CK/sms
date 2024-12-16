import json

import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from student_management_app.forms import AddStudentForm, EditStudentForm
from student_management_app.models import (
    Attendance,
    AttendanceReport,
    Courses,
    CustomUser,
    FeedBackStaffs,
    FeedBackStudent,
    LeaveReportStaff,
    LeaveReportStudent,
    NotificationStaffs,
    NotificationStudent,
    SessionYearModel,
    Staffs,
    Students,
    Subjects,
)


def admin_home(request):
    student_count1 = Students.objects.all().count()
    staff_count = Staffs.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()

    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []
    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subjects_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)

    staffs = Staffs.objects.all()
    attendance_present_list_staff = []
    attendance_absent_list_staff = []
    staff_name_list = []
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(
            subject_id__in=subject_ids,
        ).count()
        leaves = LeaveReportStaff.objects.filter(
            staff_id=staff.id, leave_status=1
        ).count()
        attendance_present_list_staff.append(attendance)
        attendance_absent_list_staff.append(leaves)
        staff_name_list.append(staff.admin.username)

    students_all = Students.objects.all()
    attendance_present_list_student = []
    attendance_absent_list_student = []
    student_name_list = []
    for student in students_all:
        attendance = AttendanceReport.objects.filter(
            student_id=student.id, status=True
        ).count()
        absent = AttendanceReport.objects.filter(
            student_id=student.id, status=False
        ).count()
        leaves = LeaveReportStudent.objects.filter(
            student_id=student.id, leave_status=1
        ).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves + absent)
        student_name_list.append(student.admin.username)

    return render(
        request,
        "hod_template/home_content.html",
        {
            "student_count": student_count1,
            "staff_count": staff_count,
            "subject_count": subject_count,
            "course_count": course_count,
            "course_name_list": course_name_list,
            "subject_count_list": subject_count_list,
            "student_count_list_in_course": student_count_list_in_course,
            "student_count_list_in_subject": student_count_list_in_subject,
            "subject_list": subject_list,
            "staff_name_list": staff_name_list,
            "attendance_present_list_staff": attendance_present_list_staff,
            "attendance_absent_list_staff": attendance_absent_list_staff,
            "student_name_list": student_name_list,
            "attendance_present_list_student": attendance_present_list_student,
            "attendance_absent_list_student": attendance_absent_list_student,
        },
    )


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")

        try:
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                last_name=last_name,
                first_name=first_name,
                user_type=2,
            )
            user.staffs.address = address
            user.save()
            messages.success(request, "Successfully Added Staff")
            return HttpResponseRedirect(reverse("add_staff"))
        except Exception:
            messages.error(request, "Failed to Add Staff")
            return HttpResponseRedirect(reverse("add_staff"))


def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course = request.POST.get("course")
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Successfully Added Course")
            return HttpResponseRedirect(reverse("add_course"))
        except Exception as e:
            print(e)
            messages.error(request, "Failed To Add Course")
            return HttpResponseRedirect(reverse("add_course"))


def add_student(request):
    form = AddStudentForm()
    return render(
        request,
        "hod_template/add_student_template.html",
        {"form": form},
    )


def add_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        form = AddStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            address = form.cleaned_data["address"]
            session_year_id = form.cleaned_data["session_year_id"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]

            profile_pic = request.FILES["profile_pic"]
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)

            try:
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    last_name=last_name,
                    first_name=first_name,
                    user_type=3,
                    profile_pic=profile_pic_url,
                )
                user.students.address = address
                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj
                session_year = SessionYearModel.object.get(id=session_year_id)
                user.students.session_year_id = session_year
                user.students.gender = sex
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except Exception:
                messages.error(request, "Failed to Add Student")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form = AddStudentForm(request.POST)
            return render(
                request,
                "hod_template/add_student_template.html",
                {"form": form},
            )


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(
        request,
        "hod_template/add_subject_template.html",
        {"staffs": staffs, "courses": courses},
    )


def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        course = Courses.objects.get(id=course_id)
        staff_id = request.POST.get("staff")
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(
                subject_name=subject_name, course_id=course, staff_id=staff
            )
            subject.save()
            messages.success(request, "Successfully Added Subject")
            return HttpResponseRedirect(reverse("add_subject"))
        except Exception:
            messages.error(request, "Failed to Add Subject")
            return HttpResponseRedirect(reverse("add_subject"))


def manage_staff(request):
    staffs = Staffs.objects.all()
    return render(
        request, "hod_template/manage_staff_template.html", {"staffs": staffs}
    )


def manage_student(request):
    students = Students.objects.all()
    return render(
        request,
        "hod_template/manage_student_template.html",
        {"students": students},
    )


def manage_course(request):
    courses = Courses.objects.all()
    return render(
        request,
        "hod_template/manage_course_template.html",
        {"courses": courses},
    )


def manage_subject(request):
    subjects = Subjects.objects.all()
    return render(
        request,
        "hod_template/manage_subject_template.html",
        {"subjects": subjects},
    )


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    return render(
        request,
        "hod_template/edit_staff_template.html",
        {"staff": staff, "id": staff_id},
    )


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get("staff_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        address = request.POST.get("address")

        try:
            user = CustomUser.objects.get(id=staff_id)

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()

            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()
            messages.success(request, "Successfully Edited Staff")
            return HttpResponseRedirect(
                reverse("edit_staff", kwargs={"staff_id": staff_id})
            )
        except Exception:
            messages.error(request, "Could Not Update")
            return HttpResponseRedirect(
                reverse("edit_staff", kwargs={"staff_id": staff_id})
            )


def edit_student(request, student_id):
    request.session["student_id"] = student_id
    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    form.fields["email"].initial = student.admin.email
    form.fields["first_name"].initial = student.admin.first_name
    form.fields["last_name"].initial = student.admin.last_name
    form.fields["username"].initial = student.admin.username
    form.fields["address"].initial = student.address
    form.fields["course"].initial = student.course_id.id
    form.fields["sex"].initial = student.gender
    form.fields["session_year_id"].initial = student.session_year_id.id
    return render(
        request,
        "hod_template/edit_student_template.html",
        {"form": form, "id": student_id, "username": student.admin.username},
    )


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id = request.session.get("student_id")
        if student_id is None:
            return HttpResponseRedirect(reverse("manage_student"))

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            session_year_id = form.cleaned_data["session_year_id"]
            course_id = form.cleaned_data["course"]
            sex = form.cleaned_data["sex"]

            if request.FILES.get("profile_pic", False):
                profile_pic = request.FILES["profile_pic"]
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.email = email
                user.save()

                student = Students.objects.get(admin=student_id)
                student.address = address
                session_year = SessionYearModel.object.get(id=session_year_id)
                student.session_year_id = session_year
                student.gender = sex
                course = Courses.objects.get(id=course_id)
                student.course_id = course
                if profile_pic_url is not None:
                    student.profile_pic = profile_pic_url
                student.save()
                del request.session["student_id"]
                messages.success(request, "Successfully Edited Student")
                return HttpResponseRedirect(
                    reverse("edit_student", kwargs={"student_id": student_id})
                )
            except Exception:
                messages.error(request, "Failed to Edit Student")
                return HttpResponseRedirect(
                    reverse("edit_student", kwargs={"student_id": student_id})
                )
        else:
            form = EditStudentForm(request.POST)
            student = Students.objects.get(admin=student_id)
            return render(
                request,
                "hod_template/edit_student_template.html",
                {
                    "form": form,
                    "id": student_id,
                    "username": student.admin.username,
                },
            )


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    return render(
        request,
        "hod_template/edit_subject_template.html",
        {
            "subject": subject,
            "staffs": staffs,
            "courses": courses,
            "id": subject_id,
        },
    )


def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id = request.POST.get("subject_id")
        subject_name = request.POST.get("subject_name")
        staff_id = request.POST.get("staff")
        course_id = request.POST.get("course")

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            course = Courses.objects.get(id=course_id)
            subject.course_id = course
            subject.save()

            messages.success(request, "Successfully Edited Subject")
            return HttpResponseRedirect(
                reverse("edit_subject", kwargs={"subject_id": subject_id})
            )
        except Exception:
            messages.error(request, "Failed to Edit Subject")
            return HttpResponseRedirect(
                reverse("edit_subject", kwargs={"subject_id": subject_id})
            )


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    return render(
        request,
        "hod_template/edit_course_template.html",
        {"course": course, "id": course_id},
    )


def edit_course_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id = request.POST.get("course_id")
        course_name = request.POST.get("course")

        try:
            course = Courses.objects.get(id=course_id)
            print(Courses.course_name)
            course.course_name = course_name
            course.save()
            messages.success(request, "Successfully Edited Course")
            return HttpResponseRedirect(
                reverse("edit_course", kwargs={"course_id": course_id})
            )
        except Exception:
            messages.error(request, "Failed to Edit Course")
            return HttpResponseRedirect(
                reverse("edit_course", kwargs={"course_id": course_id})
            )


def manage_session(request):
    return render(request, "hod_template/manage_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_session"))
    else:
        session_start_year = request.POST.get("session_start")
        session_end_year = request.POST.get("session_end")

        try:
            sessionyear = SessionYearModel(
                session_start_year=session_start_year,
                session_end_year=session_end_year,
            )
            sessionyear.save()
            messages.success(request, "Successfully Added Session")
            return HttpResponseRedirect(reverse("manage_session"))
        except Exception:
            messages.error(request, "Failed to Add Session")
            return HttpResponseRedirect(reverse("manage_session"))


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    return render(
        request,
        "hod_template/staff_feedback_template.html",
        {"feedbacks": feedbacks},
    )


def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    return render(
        request,
        "hod_template/student_feedback_template.html",
        {"feedbacks": feedbacks},
    )


@csrf_exempt
def student_feedback_message_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_message
        feedback.save()
        return HttpResponse("True")
    except Exception:
        return HttpResponse("False")


@csrf_exempt
def staff_feedback_message_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_message
        feedback.save()
        return HttpResponse("True")
    except Exception:
        return HttpResponse("False")


@csrf_exempt
def staff_leave_view(request):
    if request.method == "GET":
        leaves = LeaveReportStaff.objects.all()
        context = {"leaves": leaves, "page_title": "Leave Applications From Staff"}
        return render(request, "hod_template/staff_leave_view.html", context)

    elif request.method == "POST":
        leave_id = request.POST.get("id")
        status = request.POST.get("status")

        try:
            status = int(status)
            if status not in [1, -1]:
                raise ValueError("Invalid status value")
        except ValueError:
            return JsonResponse(
                {"success": False, "message": "Invalid status value"}, status=400
            )

        try:
            leave = get_object_or_404(LeaveReportStaff, id=leave_id)
            leave.leave_status = status
            leave.save()
            return JsonResponse(
                {"success": True, "message": "Leave status updated successfully"}
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": f"An error occurred: {str(e)}"},
                status=500,
            )


@csrf_exempt
def student_leave_view(request):
    if request.method == "GET":
        leaves = LeaveReportStudent.objects.all()
        context = {"leaves": leaves, "page_title": "Leave Applications From Students"}
        return render(request, "hod_template/student_leave_view.html", context)

    elif request.method == "POST":
        leave_id = request.POST.get("id")
        status = request.POST.get("status")

        if not leave_id:
            return JsonResponse(
                {"success": False, "message": "Leave ID is required"}, status=400
            )

        if not status:
            return JsonResponse(
                {"success": False, "message": "Status is required"}, status=400
            )

        try:
            status = int(status)
            if status not in [1, -1]:
                return JsonResponse(
                    {"success": False, "message": "Invalid status value"}, status=400
                )
        except ValueError:
            return JsonResponse(
                {"success": False, "message": "Status must be a number"}, status=400
            )

        try:
            leave = get_object_or_404(LeaveReportStudent, id=leave_id)
            leave.leave_status = status  # Changed from status to leave_status
            leave.save()

            status_text = "approved" if status == 1 else "rejected"
            return JsonResponse(
                {
                    "success": True,
                    "message": f"Leave application has been {status_text} successfully",
                }
            )

        except LeaveReportStudent.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Leave application not found"}, status=404
            )
        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": "An error occurred while processing the request",
                },
                status=500,
            )

    return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_year_id = SessionYearModel.object.all()
    return render(
        request,
        "hod_template/admin_view_attendance.html",
        {"subjects": subjects, "session_year_id": session_year_id},
    )


@csrf_exempt
def admin_get_attendance_dates(request):
    subject = request.POST.get("subject")
    session_year_id = request.POST.get("session_year_id")
    subject_obj = Subjects.objects.get(id=subject)
    session_year_obj = SessionYearModel.object.get(id=session_year_id)
    attendance = Attendance.objects.filter(
        subject_id=subject_obj, session_year_id=session_year_obj
    )
    attendance_obj = []
    for attendance_single in attendance:
        data = {
            "id": attendance_single.id,
            "attendance_date": str(attendance_single.attendance_date),
            "session_year_id": attendance_single.session_year_id.id,
        }
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj), safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        data_small = {
            "id": student.student_id.admin.id,
            "name": student.student_id.admin.first_name
            + " "
            + student.student_id.admin.last_name,
            "status": student.status,
        }
        list_data.append(data_small)
    return JsonResponse(
        json.dumps(list_data), content_type="application/json", safe=False
    )


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(
        request,
        "hod_template/admin_profile.html",
        {"user": user},
    )


def admin_profile_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("admin_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        # password = request.POST.get("password")
        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            # if password!=None and password!="":
            #     customuser.set_password(password)
            customuser.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))
        except Exception:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("admin_profile"))


def admin_send_notification_student(request):
    students = Students.objects.all()
    return render(
        request,
        "hod_template/student_notification.html",
        {"students": students},
    )


def admin_send_notification_staff(request):
    staffs = Staffs.objects.all()
    return render(
        request,
        "hod_template/staff_notification.html",
        {"staffs": staffs},
    )


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")
    student = get_object_or_404(Students, admin=id)
    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "notification": {
            "title": "Student Management System",
            "body": message,
            "click_action": reverse("student_all_notification"),
            "icon": static("dist/img/logo.png"),
        },
        "to": student.admin.fcm_tocken,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB",
    }
    data = requests.post(url, data=json.dumps(body), headers=headers)
    notification = NotificationStudent(student_id=student, message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")
    staff = get_object_or_404(Staffs, admin=id)
    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "notification": {
            "title": "Student Management System",
            "body": message,
            "click_action": reverse("staff_all_notification"),
            "icon": static("dist/img/logo.png"),
        },
        "to": staff.admin.fcm_token,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB",
    }
    data = requests.post(url, data=json.dumps(body), headers=headers)
    notification = NotificationStaffs(staff_id=staff, message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")


def delete_course(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request,
            "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again",
        )
    return redirect(reverse("manage_course"))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse("manage_subject"))


def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse("manage_staff"))


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse("manage_student"))


def delete_session(request, session_id):
    session = get_object_or_404(SessionYearModel, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request,
            "There are students assigned to this session. Please move them to another session.",
        )
    return redirect(reverse("manage_session"))
