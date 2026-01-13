from django.contrib import admin
from .models import Trainer, Student, Attendance

admin.site.register(Trainer)
admin.site.register(Student)
admin.site.register(Attendance)
