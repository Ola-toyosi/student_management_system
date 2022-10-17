from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import AddStudentForm, EditStudentForm

from .models import CustomUser, Staff, Courses, Subjects, Students, SessionYearModel, FeedbackStudent, FeedbackStaff, \
    LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport


def admin_home(request):
    # get all model counts
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staff.objects.all().count()

    # get subjects under each course and students taking each course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    # get students taking each subject
    subjects_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []

    for subject in subjects_all:
        course = Courses.objects.filter(id=subject.course_id)
        subject_name = Subjects.objects.filter(course_id=course.id).count()
        student_count = Students.objects.filter(course_id=course.id)
        subject_list.append(subject_name)
        student_count_list_in_subject.append(student_count)

    #     For Staff
    staff_name_list = []
    staff_attendance_present_list = []
    staff_attendance_leave_list = []

    staffs = Staff.objects.all()
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id).count()
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leave = LeaveReportStaff.objects.filter(staff_id=staff.id,
                                                leave_status=1).count()
        staff_name_list.append(staff.admin.first_name)
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leave)

    #     For Students
    student_name_list = []
    student_attendance_present_list = []
    student_attendance_leave_list = []

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id,
                                                     status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id,
                                                 status=False).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id,
                                                  leave_status=1).count()
        student_name_list.append(student.admin.first_name)
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave + absent)

    context = {
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_attendance_present_list": staff_attendance_present_list,
        "student_name_list": student_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
    }

    return render(request, "hod_template/home_content.html", context)


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, 'Invalid method')
        return redirect("add_staff")
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username,
                                                  first_name=first_name,
                                                  last_name=last_name,
                                                  email=email,
                                                  password=password,
                                                  user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to add staff")
            return redirect('add_staff')


def manage_staff(request):
    staffs = Staff.objects.all()
    context = {
        "staff": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staff.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            #             Insert into customer data
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.save()

            staff_model = Staff.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, 'Staff Updated Successfully')
            return redirect('/edit_save/' + staff_id)

        except:
            messages.error(request, 'Failed to update staff record')
            return redirect('/edit_save/' + staff_id)


def delete_staff(request, staff_id):
    staff = Staff.objects.get(admin=staff_id)

    try:
        staff.delete()
        messages.success(request, 'Staff Deleted Successfully')
        return redirect('manage_staff')
    except:
        messages.error(request, 'Failed to delete staff record')
        return redirect('manage_staff')


def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, 'Invalid method')
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to add course")
            return redirect('add_course')


def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, "hod_template/manage_course_template.html", context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, "hod_template/edit_course_template.html", context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully")
            return redirect('edit_course')
        except:
            messages.error(request, "Failed to update course")
            return redirect('edit_course')


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)

    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to delete Course")
        return redirect('manage_course')


def add_session(request):
    return render(request, "hod_templates/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid method")
        return redirect('add_session')
    else:
        session_start_year = request.POST.get('session_star_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year,
                                           session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, 'Session Year Added Successfully')
            return redirect('add_save')
        except:
            messages.error(request, 'Failed to add Session Year')
            return redirect('add_save')


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_templates/manage_session_template.html", context)


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_templates/edit_session_year.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid method")
        return redirect('edit_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_end_year = session_end_year
            session_year.session_start_year = session_start_year
            session_year.save()

            messages.success(request, 'Session Year Updated Successfully')
            return redirect('/edit_session/' + session_id)
        except:
            messages.error(request, 'Failed to update Session Year')
            return redirect('/edit_session/' + session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, 'Deleted Success Year Successfully')
        return redirect('manage_session')
    except:
        messages.error(request, 'Failed to delete Session Year')
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template', context)


def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            course_id = form.cleaned_data['course_id']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic
            #  Check whether the file is selected or not
            # Upload only if file is selected

            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = CustomUser.objects.create_user(username=username,
                                                      password=password,
                                                      first_name=first_name,
                                                      last_name=last_name,
                                                      user_type=3)
                user.students.address = address
                user.students.gender = gender
                user.students.email = email

                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj

                session_obj = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_obj

                user.students.profile_pic = profile_pic_url

                user.save()
                messages.success(request, 'Student created successfully')
                return redirect('add_student')

            except:
                messages.error(request, 'Failed to add student')
                return redirect('add_student')

        else:
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, "hod_template/manage_student_template.html", context)


def edit_student(request, student_id):
    #     Add Student id into session variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()

    # fill form with data from database
    form.fields['email'].initial = student.admin.email
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['username'].initial = student.admin.username
    form.fields['address'].initial = student.admin.address
    form.fields['course_id'].initial = student.admin.course_id
    form.fields['gender'].initial = student.admin.gender
    form.fields['session_year_id'].initial = student.admin.session_year_id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }

    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        HttpResponse('Invalid response')
    else:
        student_id = Students.objects.get('student_id')
        if student_id is None:
            return redirect('manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']

            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                #  first update custom user model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username

                #     update students table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                course = Courses.objects.get(id=course_id)
                student_model.course_id = course

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url

                student_model.save()

                del request.session['student_id']

                messages.success(request, 'Student data updated successfully')
                return redirect('/edit_student/' + student_id)

            except:
                messages.error(request, 'Student data failed to update')
                return redirect('/edit_student/' + student_id)


def delete_student(request, student_id):
    student = Students.objects.get(id=student_id)
    try:
        student.delete()
        messages.success(request, 'Student Record Deleted Successfully')
        return redirect('manage_student')
    except:
        messages.error(request, 'Failed to delete student record')
        return redirect('manage_student')


def add_subject(request):
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs
    }
    return render(request, 'hod_template/add_subject_template.html', context)


def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, 'Method not allowed.')
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name,
                               course_id=course,
                               staff_id=staff)
            subject.save()
            messages.success(request, 'Subject Added Successfully!')
            return redirect('add_subject')
        except:
            messages.error(request, 'Failed to Add Subjects!')
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }

    return redirect(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "id": subject_id,
        "subject": subject,
        "courses": courses,
        "staffs": staffs
    }
    return render(request, "hod_tenplate/edit_subject_template.html", context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse('Invalid Method')
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject_name')
        course_id = request.POST.get('course_id')
        staff_id = request.POST.get('staff_id')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            staff = Staff.objects.get(id=staff_id)
            subject.staff_id = staff

            subject.save()

            messages.success(request, 'Subject updated successfully!')
            return HttpResponseRedirect(reverse("edit_subject",
                                                kwargs={"subject_id": subject_id}))
        except:
            messages.error(request, 'Failed to update Subjects')
            return HttpResponseRedirect(reverse("edit_subject",
                                                kwargs={"subject_id": subject_id}))


def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, 'Subject deleted successfully')
        return redirect('manage_subject')
    except:
        messages.success(request, 'Failed to delete subject')
        return redirect('manage_subject')


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exists(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


def student_feedback_message(request):
    feedbacks = FeedbackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, "hod_template/student_feedback_template.html", context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedbackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedbackStaff.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, "hod_template/staff_feedback_template.html", context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('feedback_id')
    feedback_reply = request.POST.get('feedback_reply')

    try:
        feedback = FeedbackStaff.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse('True')
    except:
        return HttpResponse('False')


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)


def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")
    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)
    attendance = Attendance.objects.filter(subject_id=subject_model,
                                           session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    std_list_data = []

    for attendance_single in attendance:
        data_small = {"id": attendance_single.id,
                      "attendance_date": str(attendance_single.attendance_date),
                      "session_year_id": attendance_single.session_year_id.id}
        std_list_data.append(data_small)

    return JsonResponse(json.dumps(std_list_data),
                        content_type="application/json",
                        safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only

    std_list_data = []

    for student in attendance_data:
        data_small = {"id": student.student_id.admin.id,
                      "name": student.student_id.admin.first_name + " " + student.student_id.admin.last_name,
                      "status": student.status}
        std_list_data.append(data_small)

    return JsonResponse(json.dumps(std_list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context = {
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')


def staff_profile(request):
    pass


def student_profile(request):
    pass
