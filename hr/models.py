from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings

# Monthly Attendance Documents
class AttendanceDocument(models.Model):
    name = models.CharField(max_length=255, verbose_name="Document Name")
    date = models.DateField(verbose_name="Date")
    month = models.CharField(max_length=100, verbose_name="Month")

    document = CloudinaryField(
        resource_type='auto',
        folder='hr/attendance_documents/',
        null=True,
        blank=True,
        verbose_name="Attendance Document"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Attendance Document"
        verbose_name_plural = "Attendance Documents"

    def __str__(self):
        return f"{self.name} - {self.month}"

# Penalty linked directly to User
class Penalty(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="penalties"
    )
    act = models.CharField(max_length=1000, verbose_name="Reason / Act")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.CharField(max_length=100, verbose_name="Month")
    date = models.DateField()

    class Meta:
        verbose_name = "Penalty"
        verbose_name_plural = "Penalties"
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.month} - ₹{self.amount}"
