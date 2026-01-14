from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator

User = get_user_model()


class Trainer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='trainer_profile'
    )
    drive_link = models.URLField(blank=True)

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ON_LEAVE', 'On Leave'),
        ('INACTIVE', 'Inactive'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    


class Student(models.Model):
    BATCH_CHOICES = [
        ('A1', 'A1 (Beginner)'),
        ('A2', 'A2 (Elementary)'),
        ('B1', 'B1 (Intermediate)'),
        ('B2', 'B2 (Upper Intermediate)'),
        ('A1 ONLINE', 'A1 (Online)'),
        ('A2 ONLINE', 'A2 (Online)'),
        ('B1 ONLINE', 'B1 (Online)'),
        ('B2 ONLINE', 'B2 (Online)'),
        ('A1 EXAM PREPERATION', 'A1 (Exam Preparation)'),
        ('A2 EXAM PREPERATION', 'A2 (Exam Preparation)'),
        ('B1 EXAM PREPERATION', 'B1 (Exam Preparation)'),
        ('B2 EXAM PREPERATION', 'B2 (Exam Preparation)'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
    ]

    CLASS_CHOICES = [
        ('C1', 'C1'), ('C2', 'C2'), ('C3', 'C3'), ('C4', 'C4'),
        ('C5', 'C5'), ('C6', 'C6'), ('C7', 'C7'), ('C8', 'C8'),
        ('C9', 'C9'), ('C10', 'C10'), ('C11', 'C11'), ('C12', 'C12'),
        ('C13', 'C13'), ('C14', 'C14'), ('C15', 'C15'), ('C16', 'C16'),
        ('C17', 'C17'), ('C18', 'C18'), ('C19', 'C19'), ('C20', 'C20'),
        ('ONLINE', 'Online'),
    ]

    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    batch = models.CharField(max_length=200, choices=BATCH_CHOICES)
    trainer = models.ForeignKey(Trainer, on_delete=models.PROTECT, related_name='students')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    admission_date = models.DateField()
    notes = models.TextField(blank=True)

    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    drive_link = models.URLField(blank=True, null=True)
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ['batch', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_batch_display()})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('NO_SESSION', 'No Session'),
    ]

    date = models.DateField()
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PRESENT')
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__name']
        indexes = [
            models.Index(fields=['date', 'trainer']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'student'],
                name='unique_student_attendance_per_day'
            )
        ]

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
