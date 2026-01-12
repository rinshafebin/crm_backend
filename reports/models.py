from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import os

User = get_user_model()


def report_upload_path(instance, filename):
    return os.path.join("daily_reports", str(instance.user.id), filename)


class DailyReport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_reports',
        db_index=True
    )

    name = models.CharField(max_length=200)
    heading = models.CharField(max_length=300)
    report_text = models.TextField()

    # Local file upload for testing
    attached_file = models.FileField(
        upload_to=report_upload_path,
        null=True,
        blank=True
    )

    report_date = models.DateField(
        default=timezone.now,
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_reports'
    )

    review_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date', '-created_at']
        unique_together = ('user', 'report_date')
        indexes = [
            models.Index(fields=['user', 'report_date']),
            models.Index(fields=['status', 'report_date']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.report_date}"

    def get_file_url(self):
        if self.attached_file:
            return self.attached_file.url
        return None
