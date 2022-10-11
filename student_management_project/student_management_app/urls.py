from django.contrib import admin
from django.urls import path, include
from . import views
from . import HodViews, StaffViews, StudentViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('contact', views.contact, name="contact"),
    path('login', views.loginUser, name="login"),
    path('logout_user', views.logout_user, name="logout_user"),
    path('registration', views.registration, name="registration"),
    path('doLogin', views.doLogin, name="doLogin"),
    path('doRegistration', views.doRegistration, name="doRegistration"),

    #     STUDENT URLS
    path('student_home', StudentViews.student_home, name="student_home"),
    path('student_attendance', StudentViews.student_attendance, name="student_attendance"),
    path('student_attendance_post', StudentViews.student_attendance_post, name="student_attendance_post"),
    path('student_apply_leave', StudentViews.student_apply_leave, name="student_apply_leave"),
    path('student_apply_leave_save', StudentViews.student_apply_leave_save, name="student_apply_leave_save"),
    path('student_feedback', StudentViews.student_feedback, name="student_feedback"),
    path('student_feedback_save', StudentViews.student_feedback_save, name="student_feedback_save"),
    path('student_profile', StudentViews.student_profile, name="student_profile"),
    path('student_profile_update', StudentViews.student_profile_update, name="student_profile_update"),
]
