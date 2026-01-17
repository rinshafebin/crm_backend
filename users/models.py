from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from django.db import models
from django.conf import settings
 

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'General Manager'),
        ('OPS', 'Operations Manager'),
        ('ADM_MANAGER', 'Admission Manager'),
        ('ADM_EXEC', 'Admission Executive'),
        ('PROCESSING', 'Processing Executive'),
        ('MEDIA', 'Media Team'),
        ('TRAINER', 'Trainer'),
        ('BUSINESS_HEAD', 'Business Head'),
        ('BDM', 'Business Development Manager'),
        ('CM', 'Center Manager'),
        ('HR', 'Human Resources'),
        ('FOE', 'FOE Cum TC'),
    ]

    role = models.CharField(max_length=100, choices=ROLE_CHOICES,db_index=True )
    team = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)


    # Add these lines to resolve clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_groups",  
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",  
        related_query_name="user",
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_business_head(self):
        return self.role == 'BUSINESS_HEAD'    

    @property 
    def is_cm(self):   
        return self.role == 'CM'

    @property
    def is_hr(self):
        return self.role == 'HR'


class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ("LEAD_CREATED", "Lead Created"),
        ("STUDENT_ENROLLED", "Student Enrolled"),
        ("TASK_COMPLETED", "Task Completed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.description