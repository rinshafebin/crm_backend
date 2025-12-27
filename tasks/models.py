from django.db import models
from django.utils import timezone
from users.models import User

class Task(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'role__in': ['BUSINESS_HEAD', 'ADMIN', 'OPS']}
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        limit_choices_to={'role__in': ['MEDIA', 'ADM_MANAGER', 'ADM_EXEC']}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['deadline']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['completed_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Update completed_at when status changes to COMPLETED
        if self.status == 'COMPLETED' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'COMPLETED' and self.completed_at:
            self.completed_at = None
        
        
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue considering timezone"""
        if self.status in ['COMPLETED', 'CANCELLED']:
            return False
        return self.status == 'OVERDUE' or timezone.now() > self.deadline
    
    @property
    def overdue_days(self):
        """Calculate how many days overdue"""
        if self.status in ['COMPLETED', 'CANCELLED']:
            return 0
        if timezone.now() <= self.deadline:
            return 0
        delta = timezone.now() - self.deadline
        return delta.days
    
    @property
    def days_until_deadline(self):
        if timezone.now() >= self.deadline:
            return 0
        delta = self.deadline - timezone.now()
        return delta.days
    
    @classmethod
    def update_overdue_tasks(cls):
        """Update tasks that are past their deadline to OVERDUE status"""
        now = timezone.now()
        
        # Find tasks that are overdue but not already marked as OVERDUE, COMPLETED, or CANCELLED
        overdue_tasks = cls.objects.filter(
            deadline__lt=now,
            status__in=['PENDING', 'IN_PROGRESS']
        )
        
        updated_count = 0
        for task in overdue_tasks:
            # Create a TaskUpdate record to track the status change
            TaskUpdate.objects.create(
                task=task,
                updated_by=task.assigned_by,  # Use assigned_by as the system updater
                previous_status=task.status,
                new_status='OVERDUE',
                notes='Automatically marked as overdue due to deadline'
            )
            
            # Update the task status
            task.status = 'OVERDUE'
            task.save(update_fields=['status', 'updated_at'])
            updated_count += 1
        
        return updated_count

class TaskUpdate(models.Model):
    """Model to track task status updates and notes"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.title} - {self.previous_status} → {self.new_status}"