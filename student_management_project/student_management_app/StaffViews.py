from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json
from .models import CustomUser, Staff, Courses, Subjects, Students, SessionYearModel, Attendance, AttendanceReport, \
    LeaveReportStaff, FeedbackStaff, StudentResult


def staff_home(request):
    #     Fetch all students under the staff
    print(request.user.id)
    # fetch subjects taught by staff
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    print(subjects)
    # create a variable to collect course id
    course_id_list = []
    for subject in subjects:
        # fetch course id for subjects taught by staff
        course = Courses.objects.filter(id=subject.course_id.id)
        course_id_list.append(course.id)

    # create a variable to collect filtered course id
    final_course = []
    #     Removing Duplicate Course ID
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    print(final_course)
    # check students taking courses
    students_count = Students.objects.filter(course_id__in=final_course).count()
    #   find total subjects
    subject_count = subjects.count()
    print(subject_count)
    print(students_count)

    #     fetch all attendance count
    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()

    #     fetch all approved leave
    print(request.user.user_type)
    staff = Staff.objects.get(admin=request.user.id)
    leave_count = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()

    #     fetch attendance data by subjects
    subject_list = []
    attendance_list = []
    for subject in subjects:
        attendance_count_no = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count_no)

    student_attendance = Students.objects.filter(course_id__in=final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    for student in student_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True,
                                                                   student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False,
                                                                  student_id=student.id).count()
        student_list.append(student.admin.first_name + " " + student.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context = {
        "students_count": students_count,
        "attendance_count": attendance_count,
        "leave_count": leave_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent,
    }

    return render(request, "staff_template/staff_home_template.html", context)


def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years,
    }

    return render(request, "staff_template/take_attendance_template.html", context)


def staff_apply_leave(request):
    staff_obj = Staff.objects.get(admin=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_obj)
    context = {
        "leave_data": leave_data
    }

    return render(request, "staff_template/staff_apply_leave_template.html", context)


def staff_apply_leave_save(request):
    if request.method is not "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_apply_leave')
    else:
        leave_date = request.POST.get("leave_date")
        leave_message = request.POST.get("leave_message")

        staff_obj = Staff.objects.filter(admin=request.user.id)

        try:
            leave_report = LeaveReportStaff(staff_id=staff_obj,
                                            leave_date=leave_date,
                                            leave_message=leave_message,
                                            leave_status=0)
            leave_report.save()
            messages.success(request, "Applied for Leave.")
            return redirect('staff_apply_leave')
        except:
            messages.error(request, "Failed to apply for leave.")
            return redirect('staff_apply_leave')


def staff_feedback(request):
    return render(request, 'staff_template/staff_feedback_template.html')


def staff_feedback_save(request):
    if request.method is not "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get("feedback_reply")

        staff_obj = Staff.objects.filter(admin=request.user.id)

        try:
            add_feedback = LeaveReportStaff(staff_id=staff_obj,
                                            feedback=feedback,
                                            feedback_reply=" ", )
            add_feedback.save()
            messages.success(request, "Feedback sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to send feedback.")
            return redirect('staff_feedback')


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get("subject_id")
    session_year = request.POST.get("session_year")

    #      Students enroll to course, Course have subjects
    #       getting subject model using subject_id

    subject_model = Subjects.objects.filter(id=subject_id)
    session_model = SessionYearModel.objects.filter(id=session_year)

    students = Students.objects.filter(course_id=subject_model.course_id,
                                       session_year_id=session_model)

    #     pass only the student id and student name
    std_list_data = []

    for student in students:
        data_small = {
            "id": student.admin.id,
            "name": student.admin.first_name + " " + student.admin.last_name,
        }

        std_list_data.append(data_small)

    return JsonResponse(json.dumps(std_list_data), content_type="application./json", safe=False)


@csrf_exempt
def save_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    subject_model = Subjects.objects.filter(id=subject_id)
    session_year_model = SessionYearModel.objects.filter(id=session_year_id)

    json_student = json.load(student_ids)

    try:
        # save attendance to attendance model
        attendance = Attendance(subject_id=subject_model,
                                attendance_date=attendance_date,
                                session_year_id=session_year_model)
        attendance.save()

        #         save student attendance to attendanceReport model

        for stud in json_student:
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(student_id=student,
                                                 attendance_id=attendance,
                                                 status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")

    except:
        return HttpResponse('Error')


def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()

    context = {
        "subjects": subjects,
        "session_years": session_years,
    }

    return render(request, "staff_template/update_attendance_template.html ")


@csrf_exempt
def get_attendance_dates(request):
    subject_id = request.POST.get("subject_id")
    session_year_id = request.POST.get("session_year_id")

    subject_model = Subjects.objects.get(id=subject_id)
    session_model = SessionYearModel.objects.get(id=session_year_id)

    attendance = Attendance.objects.filter(subject_id=subject_model,
                                           session_year_id=session_model)

    # pass only student id and student name

    std_list_data = []

    for attend in attendance:
        data_small = {"id": attend.id,
                      "attendance_date": str(attend.attendance_date),
                      "session_year_id": attend.session_year_id}

        std_list_data.append(data_small)

    return JsonResponse(json.dumps(std_list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_attendance_student(request):
    #   Get values from POST request
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filters(attendance_id=attendance)

    #   fetch only student id and name
    std_list_data = []

    for student in attendance_data:
        data_small = {
            "id": student.student_id.admin.id,
            "name": student.student_id.admin.first_name + " " + student.student_id.admin.last_name,
            "status": student.status
        }

        std_list_data.append(data_small)

    return JsonResponse(json.dumps(std_list_data), content_type="application/json", safe=False)


@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_student = json.loads(student_ids)

    try:
        for stud in json_student:
            student = Students.objects.filter(admin=stud["id"])
            attendance_report = AttendanceReport.objects.get(student_id=student,
                                                             attendance_id=attendance)
            attendance_report.status = stud["status"]
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staff.objects.get(admin=user)

    context = {
        "user": user,
        "staff": staff
    }

    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method is not "POST":
        messages.error(request, "Invalid method.")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password is not None and password is not "":
                customuser.set_password(password)
            customuser.save()

            staff = Staff.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')

        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')


def staff_add_result(request):
    # get subjects taught by staff
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }

    return render(request, "staff_template/add_result_template.html")


def staff_add_result_save(request):
    if request is not "POST":
        messages.error(request, "Invalid method!")
        return redirect('staff_add_result')
    else:
        student_admin_id = request.POST.get('student_list')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')
        subject_id = request.POST.get('subject')

        student_obj = Students.objects.filter(admin=student_admin_id)
        subject_obj = Subjects.objects.filter(id=subject_id)

        try:
            #             check if students result already exists
            check_exist = StudentResult.objects.filter(subject_id=subject_obj,
                                                       student_id=student_obj).exists()
            if check_exist:
                result = StudentResult.objects.get(subject_id=subject_obj,
                                                   student_id=student_obj)
                result.subject_assignment_marks = assignment_marks
                result.subject_exam_marks = exam_marks
                result.save()

                messages.success(request, "Result successfully updated!")
                return redirect('staff_add_result')

            else:
                result = StudentResult(student_id=student_obj,
                                       subject_id=subject_obj,
                                       subject_exam_marks=exam_marks,
                                       subject_assignment_marks=assignment_marks)
                result.save()
                messages.success(request, "Result Added Successfully!")
                return redirect('staff_add_result')

        except:
            messages.error(request, "Failed to Add Result!")
            return redirect('staff_add_result')
