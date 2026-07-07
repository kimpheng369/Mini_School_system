# Python Mini School Project

A Django-based Learning Management System for managing courses, lessons, assignments, enrollments, attendance, and student progress.

## Features

- User roles for employees, instructors, and students
- Course and lesson management
- Assignment submission and grading
- Student enrollment and roster management
- Review and feedback workflows
- Attendance and scheduling support

## Tech Stack

- Python
- Django
- SQLite (development)
- HTML/CSS templates

## Getting Started

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install django
   ```
4. Run database migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Demo Accounts

The project includes sample user accounts for testing:

- Employee: username `Pheng`, password `Admin3301`
- Instructor: username `teacher01`, password `Admin3301`
- Student: username `student2`, password `student3301`

## License

This project is licensed under the MIT License. See the LICENSE file for details.
