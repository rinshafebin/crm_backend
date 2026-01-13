from django.contrib import admin
from .models import Lead,ProcessingUpdate,RemarkHistory

admin.site.register(Lead)
admin.site.register(ProcessingUpdate)
admin.site.register(RemarkHistory)