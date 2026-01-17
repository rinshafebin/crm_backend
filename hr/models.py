from django.db import models
from cloudinary.models import CloudinaryField


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


class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    join_date = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    penalty = models.CharField(max_length=100, blank=True, null=True)
    attendance = models.TextField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return self.name


class Penalty(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="penalties")
    act = models.CharField(max_length=1000)
    amount = models.IntegerField(default=0, blank=True, null=True)
    month = models.CharField(max_length=100)
    date = models.DateField()

    class Meta:
        verbose_name = "Penalty"
        verbose_name_plural = "Penalties"
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.name} - {self.month} - ₹{self.amount}"
