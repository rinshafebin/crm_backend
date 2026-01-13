from django.contrib import admin
from .models import Task, TaskUpdate

# Register your models here.
admin.site.register(Task)
admin.site.register(TaskUpdate)