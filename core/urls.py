from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logged-out/', views.logout_confirmation_view, name='logged_out_confirm'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    path('employee/create_user/<str:role>/', views.create_user, name='create_user'),
    path('employee/users/<str:role>/', views.user_list, name='user_list'),
    path('employee/user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('employee/user/<int:user_id>/remove/', views.remove_user, name='remove_user'),
    path('employee/categories/', views.category_list_create, name='category_list_create'),
    path('employee/category/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('employee/category/<int:category_id>/remove/', views.remove_category, name='remove_category'),
    path('employee/courses/', views.course_list_create, name='course_list_create'),
    path('employee/enrollments/', views.manage_enrollments, name='manage_enrollments'),
    path('employee/enrollment/<int:enrollment_id>/remove/', views.remove_enrollment, name='remove_enrollment'),
    path('employee/schedules/', views.manage_schedules, name='manage_schedules'),
    path('employee/schedule/<int:schedule_id>/remove/', views.remove_schedule, name='remove_schedule'),
    path('employee/reviews/', views.view_reviews, name='view_reviews'),

    path('instructor/create_course/', views.instructor_create_course, name='instructor_create_course'),
    path('instructor/course/<int:course_id>/detail/', views.instructor_course_detail, name='instructor_course_detail'),
    path('instructor/course/<int:course_id>/student-roster/', views.view_student_roster, name='view_student_roster'),
    path('instructor/course/<int:course_id>/create_lesson/', views.create_lesson, name='create_lesson'),
    path('instructor/course/<int:course_id>/create-assignment/', views.create_assignment_or_exam, {'assignment_type': 'assignment'}, name='create_assignment'),
    path('instructor/course/<int:course_id>/create-exam/', views.create_assignment_or_exam, {'assignment_type': 'exam'}, name='create_exam'),
    path('instructor/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('instructor/submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),

    path('student/courses/', views.student_course_list, name='student_course_list'),
    path('student/course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('student/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('student/assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('student/my_grades/', views.student_my_grades, name='student_my_grades'),
    path('student/course/<int:course_id>/review/', views.add_review, name='add_review'),
]