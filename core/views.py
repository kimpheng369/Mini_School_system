from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from datetime import date
from .decorators import employee_required, instructor_required, student_required
from .models import (User, Course, Lesson, Assignment, Submission, Category, Enrollment, Review, Schedule, Attendance)
from .forms import (StudentCreationForm, UserCreationForm, UserEditForm, CourseForm, LessonForm, AssignmentForm,SubmissionForm, GradeForm, CategoryForm, ReviewForm, EnrollmentForm, ScheduleForm)

@login_required
def dashboard_redirect(request):
    if request.user.role == 'EMPLOYEE':
        return redirect('employee_dashboard')
    elif request.user.role == 'INSTRUCTOR':
        return redirect('instructor_dashboard')
    elif request.user.role == 'STUDENT':
        return redirect('student_dashboard')
    else:
        return redirect('admin:index')

def logout_confirmation_view(request):
    return render(request, 'registration/logged_out.html')

@employee_required
def employee_dashboard(request):
    student_count = User.objects.filter(role='STUDENT').count()
    instructor_count = User.objects.filter(role='INSTRUCTOR').count()
    course_count = Course.objects.count()
    enrollment_count = Enrollment.objects.count()
    recent_students = User.objects.filter(role='STUDENT').order_by('-date_joined')[:5]
    context = {
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'enrollment_count': enrollment_count,
        'recent_students': recent_students,
    }
    return render(request, 'employee/dashboard.html', context)

@employee_required
def create_user(request, role):
    if role.upper() == 'STUDENT':
        form_class = StudentCreationForm
    else:
        form_class = UserCreationForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = role.upper()
            user.save()
            messages.success(request, f"{role.title()} '{user.username}' was created successfully.")
            return redirect('user_list', role=role)
    else:
        form = form_class()

    context = {
        'form': form,
        'role': role
    }
    return render(request, 'employee/create_user.html', context)

@employee_required
def user_list(request, role):
    users = User.objects.filter(role=role.upper())
    return render(request, 'employee/user_list.html', {'users': users, 'role': role})

@employee_required
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            saved_user = form.save()
            messages.success(request, f"Successfully updated user: {saved_user.username}")
            return redirect('user_list', role=saved_user.role.lower())
    else:
        form = UserEditForm(instance=user_to_edit)
    context = {
        'form': form,
        'user_to_edit': user_to_edit
    }
    return render(request, 'employee/edit_user.html', context)

@employee_required
def remove_user(request, user_id):
    user_to_remove = get_object_or_404(User, id=user_id)
    user_role = user_to_remove.role.lower()
    if request.method == 'POST':
        username = user_to_remove.username
        user_to_remove.delete()
        messages.success(request, f"Successfully removed user: {username}")
        return redirect('user_list', role=user_role)
    context = {'user_to_remove': user_to_remove}
    return render(request, 'employee/remove_user_confirm.html', context)

@employee_required
def category_list_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list_create')
    else:
        form = CategoryForm()
    categories = Category.objects.all().order_by('name')
    context = {'form': form, 'categories': categories}
    return render(request, 'employee/category_management.html', context)

@employee_required
def course_list_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list_create')
    else:
        form = CourseForm()
    courses = Course.objects.all().select_related('category', 'instructor').order_by('title')
    context = {'form': form, 'courses': courses}
    return render(request, 'employee/course_management.html', context)
@employee_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' has been updated.")
            return redirect('category_list_create')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'employee/edit_category.html', context)


@employee_required
def remove_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category_name = category.name
        try:
            category.delete()
            messages.success(request, f"Category '{category_name}' has been removed.")
        except Exception as e:
            messages.error(request, f"Cannot delete '{category_name}'. It is still in use by one or more courses.")
        
        return redirect('category_list_create')

    context = {
        'category': category
    }
    return render(request, 'employee/remove_category_confirm.html', context)

@employee_required
def view_reviews(request):
    all_reviews = Review.objects.select_related('student', 'course', 'course__instructor').order_by('-created_at')
    context = {'reviews': all_reviews}
    return render(request, 'employee/view_reviews.html', context)

@employee_required
def manage_enrollments(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Enrollment created successfully!")
            except Exception:
                messages.error(request, "Could not create enrollment. The student may already be enrolled.")
            return redirect('manage_enrollments')
    else:
        form = EnrollmentForm()
    all_enrollments = Enrollment.objects.select_related('student', 'course', 'course__instructor').order_by('-enrolled_on')
    context = {'form': form, 'enrollments': all_enrollments}
    return render(request, 'employee/manage_enrollments.html', context)

@employee_required
def remove_enrollment(request, enrollment_id):
    if request.method == 'POST':
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        enrollment.delete()
        messages.success(request, "Enrollment removed.")
    return redirect('manage_enrollments')

@employee_required
def manage_schedules(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Schedule created successfully!")
            except Exception:
                messages.error(request, "This schedule may already exist for the course.")
            return redirect('manage_schedules')
    else:
        form = ScheduleForm()
    schedules = Schedule.objects.select_related('course').order_by('course__title', 'day_of_week')
    context = {
        'form': form,
        'schedules': schedules,
    }
    return render(request, 'employee/manage_schedules.html', context)

@employee_required
def remove_schedule(request, schedule_id):
    if request.method == 'POST':
        schedule = get_object_or_404(Schedule, id=schedule_id)
        schedule.delete()
        messages.success(request, "Schedule has been removed.")
    return redirect('manage_schedules')

@instructor_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user).annotate(
        student_count=Count('enrollment', distinct=True),
    ).order_by('-created_at')
    
    submissions_to_grade = Submission.objects.filter(
        assignment__course__instructor=request.user, 
        grade__isnull=True
    ).select_related('student', 'assignment', 'assignment__course').order_by('submitted_at')

    day_order = {'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6, 'SUN': 7}
    instructor_schedules = Schedule.objects.filter(
        course__instructor=request.user
    ).select_related('course').order_by('start_time')
    sorted_schedules = sorted(instructor_schedules, key=lambda s: day_order.get(s.day_of_week, 8))
    context = {
        'courses': courses,
        'submissions_to_grade': submissions_to_grade,
        'schedules': sorted_schedules,
        'today': date.today(),
    }
    return render(request, 'instructor/dashboard.html', context)

@instructor_required
def instructor_create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    context = {'form': form}
    return render(request, 'instructor/create_course.html', context)

@instructor_required
def instructor_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lessons = course.lessons.all().order_by('order')
    assignments = course.assignments.all()
    context = {'course': course, 'lessons': lessons, 'assignments': assignments}
    return render(request, 'instructor/course_detail.html', context)

@instructor_required
def view_student_roster(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    enrollments = Enrollment.objects.filter(course=course).select_related('student').order_by('student__last_name')
    context = {'course': course, 'enrollments': enrollments}
    return render(request, 'instructor/student_roster.html', context)

@instructor_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f"Lesson '{lesson.title}' was created successfully.")
            return redirect('instructor_course_detail', course_id=course.id)
    else:
        form = LessonForm()
    context = {
        'form': form,
        'course': course
    }
    return render(request, 'instructor/create_lesson.html', context)

@instructor_required
def create_assignment_or_exam(request, course_id, assignment_type):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    type_display = assignment_type.capitalize()
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.course = course
            instance.assignment_type = assignment_type.upper()
            instance.save()
            messages.success(request, f"{type_display} '{instance.title}' was created successfully.")
            return redirect('instructor_course_detail', course_id=course.id)
    else:
        form = AssignmentForm()
    context = {'form': form, 'course': course, 'type_display': type_display}
    return render(request, 'instructor/create_assignment.html', context)

@instructor_required
def take_attendance(request, schedule_id, date_str):
    schedule = get_object_or_404(Schedule, id=schedule_id, course__instructor=request.user)
    try:
        attendance_date = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        messages.error(request, "Invalid date format provided.")
        return redirect('instructor_dashboard')
    enrolled_students = User.objects.filter(enrollment__course=schedule.course)
    if request.method == 'POST':
        present_student_ids = request.POST.getlist('present_students')
        
        for student in enrolled_students:
            Attendance.objects.update_or_create(
                schedule=schedule, 
                student=student, 
                date=attendance_date,
                defaults={'is_present': (str(student.id) in present_student_ids)}
            )
        
        messages.success(request, f"Attendance for {attendance_date.strftime('%B %d, %Y')} has been saved.")
        return redirect('instructor_dashboard')
    attendance_list = []
    for student in enrolled_students:
        record, created = Attendance.objects.get_or_create(
            schedule=schedule, student=student, date=attendance_date,
            defaults={'is_present': False}
        )
        attendance_list.append(record)

    context = {
        'schedule': schedule,
        'attendance_date': attendance_date,
        'attendance_list': attendance_list,
    }
    return render(request, 'instructor/take_attendance.html', context)

@instructor_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=request.user)
    submissions = assignment.submissions.select_related('student').all()
    context = {'assignment': assignment, 'submissions': submissions}
    return render(request, 'instructor/view_submissions.html', context)

@instructor_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, assignment__course__instructor=request.user)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('view_submissions', assignment_id=submission.assignment.id)
    else:
        form = GradeForm(instance=submission)
    context = {'form': form, 'submission': submission}
    return render(request, 'instructor/grade_submission.html', context)

@student_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course', 'course__instructor')
    graded_submissions = Submission.objects.filter(student=request.user, grade__isnull=False)
    grade_stats = graded_submissions.aggregate(average_grade=Avg('grade'), graded_count=Count('id'))
    recent_grades = graded_submissions.order_by('-assignment__due_date')[:3]
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    day_order = {'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6, 'SUN': 7}
    student_schedules = Schedule.objects.filter(
        course_id__in=enrolled_course_ids
    ).select_related('course').order_by('start_time')
    sorted_schedules = sorted(student_schedules, key=lambda s: day_order.get(s.day_of_week, 8))
    context = {
        'enrollments': enrollments,
        'average_grade': grade_stats.get('average_grade'),
        'graded_count': grade_stats.get('graded_count'),
        'recent_grades': recent_grades,
        'schedules': sorted_schedules,
    }
    return render(request, 'student/dashboard.html', context)

@student_required
def student_course_list(request):
    all_courses = Course.objects.select_related('category', 'instructor').all()
    enrolled_course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
    context = {'courses': all_courses, 'enrolled_course_ids': enrolled_course_ids}
    return render(request, 'student/course_list.html', context)

@student_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    if created:
        messages.success(request, f"You have successfully enrolled in '{course.title}'.")
    else:
        messages.info(request, f"You are already enrolled in '{course.title}'.")
    return redirect('student_dashboard')

@student_required
def student_course_detail(request, course_id):
    enrollment = get_object_or_404(Enrollment, student=request.user, course_id=course_id)
    course = enrollment.course
    lessons = course.lessons.all().order_by('order')
    assignments = course.assignments.all()
    assignments_with_submissions = []
    for assignment in assignments:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        assignments_with_submissions.append({
            'assignment': assignment,
            'submission': submission
        })
    context = {
        'course': course,
        'lessons': lessons,
        'assignments_with_submissions': assignments_with_submissions,
    }
    return render(request, 'student/course_detail.html', context)

@student_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not Enrollment.objects.filter(student=request.user, course=assignment.course).exists():
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission, created = Submission.objects.update_or_create(
                assignment=assignment,
                student=request.user,
                defaults={'submitted_file': form.cleaned_data['submitted_file']}
            )
            messages.success(request, "Your submission has been received!")
            return redirect('student_course_detail', course_id=assignment.course.id)
    else:
        form = SubmissionForm()
    return render(request, 'student/submit_assignment.html', {'form': form, 'assignment': assignment})

@student_required
def student_my_grades(request):
    submissions = Submission.objects.filter(student=request.user, grade__isnull=False).select_related('assignment', 'assignment__course').order_by('-submitted_at')
    context = {'submissions': submissions}
    return render(request, 'student/my_grades.html', context)

@student_required
def add_review(request, course_id):
    enrollment = get_object_or_404(Enrollment, student=request.user, course_id=course_id)
    course = enrollment.course
    try:
        review = Review.objects.get(student=request.user, course=course)
    except Review.DoesNotExist:
        review = None
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.student = request.user
            new_review.course = course
            new_review.save()
            messages.success(request, "Your review has been submitted!")
            return redirect('student_course_detail', course_id=course.id)
    else:
        form = ReviewForm(instance=review)
    context = {'form': form, 'course': course}
    return render(request, 'student/add_review.html', context)