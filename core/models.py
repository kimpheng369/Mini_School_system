from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        STUDENT = "STUDENT", "Student"
    role = models.CharField(max_length=50, choices=Role.choices)
    student_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True, 
        help_text="Required only for students."
    )
    date_of_birth = models.DateField(
        blank=True, 
        null=True
    )
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='courses')
    instructor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': User.Role.INSTRUCTOR}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(help_text="Order in which the lesson appears.")
    class Meta:
        ordering = ['order']
    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}: {self.title}"
    
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.STUDENT})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('student', 'course')
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    def __str__(self):
        return self.title
    def get_submission_for_student(self, student):
        return self.submissions.filter(student=student).first()

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.STUDENT})
    submitted_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True, help_text="Grade in percentage, e.g., 85.5")
    feedback = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.STUDENT})
    rating = models.PositiveIntegerField(help_text="Rating from 1 to 5.")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Review for {self.course.title} by {self.student.username}"
    
class Schedule(models.Model):
    class DayOfWeek(models.TextChoices):
        MONDAY = "MON", "Monday"
        TUESDAY = "TUE", "Tuesday"
        WEDNESDAY = "WED", "Wednesday"
        THURSDAY = "THU", "Thursday"
        FRIDAY = "FRI", "Friday"
        SATURDAY = "SAT", "Saturday"
        SUNDAY = "SUN", "Sunday"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('course', 'day_of_week', 'start_time')
        ordering = ['course', 'day_of_week']

    def __str__(self):
        return f"{self.course.title} on {self.get_day_of_week_display()} at {self.start_time.strftime('%I:%M %p')}"
    
class Attendance(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.STUDENT})
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    class Meta:
        unique_together = ('schedule', 'student', 'date')
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.username} on {self.date} for {self.schedule.course.title} - {status}"
    
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Main description or content for the lesson.")
    order = models.PositiveIntegerField(help_text="Order in which the lesson appears.")
    video_url = models.URLField(
        blank=True, 
        null=True, 
        help_text="Optional: A URL to a video on YouTube, Vimeo, etc."
    )
    video_file = models.FileField(
        upload_to='lesson_videos/', 
        blank=True, 
        null=True, 
        help_text="Optional: Upload a video file directly."
    )
    resource_file = models.FileField(
        upload_to='lesson_resources/', 
        blank=True, 
        null=True, 
        help_text="Optional: Upload a PDF or other document."
    )
    class Meta:
        ordering = ['order']
    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}: {self.title}"
