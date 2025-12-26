from django.db import models
from users.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator

class Lead(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'), 
        ('LOW', 'Low')
    ]
    
    SOURCE_CHOICES = [
        ('WHATSAPP', 'WhatsApp'),
        ('INSTAGRAM', 'Instagram'),
        ('WEBSITE', 'Website'),
        ('WALK_IN', 'Walk-in'),
        ('AUTOMATION', 'automation'),
        ('OTHER', 'Other')
    ]
        
    PROCESSING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FORWARDED', 'Forwarded to Processing'),
        ('ACCEPTED', 'Accepted by Processing'),
        ('PROCESSING', 'In Processing'),
        ('COMPLETED', 'Processing Completed'),
        ('REJECTED', 'Processing Rejected')
    ]

    DOCUMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COLLECTED', 'Collected'),
        ('VERIFIED', 'Verified'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]

    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    phone = models.CharField(max_length=15, validators=[MinLengthValidator(10)],unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # Changed from CharField with choices to TextField
    status = models.TextField(default='ENQUIRY', help_text="Current status of the lead")
    program = models.CharField(max_length=2000, blank=True, null=True, help_text="Enter the program name")
    remarks = models.TextField(blank=True, null=True, help_text="Additional notes or comments about the lead")
    location = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    custom_source = models.CharField(max_length=50, blank=True, null=True)
    
    # Processing workflow fields
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES,default='PENDING')
    processing_executive = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'PROCESSING'},related_name='processing_leads')
    processing_status_date = models.DateTimeField(auto_now_add=True)
    processing_notes = models.TextField(blank=True, null=True)
    
    # Document tracking
    document_status = models.CharField(max_length=20, choices=DOCUMENT_STATUS_CHOICES, default='PENDING')
    documents_received = models.TextField(blank=True, null=True)
    
    # Assignment tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True,limit_choices_to={'role__in': [ 'ADM_MANAGER', 'ADM_EXEC' ] },related_name='assigned_leads')
    assigned_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    registration_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        indexes = [
            models.Index(fields=['status']),  
            models.Index(fields=['priority']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone}) - {self.status}" 

    def save(self, *args, **kwargs):
        # Update registration date when status changes to REGISTERED
        if self.status == 'REGISTERED' and not self.registration_date:
            self.registration_date = timezone.now()
        
        # Update processing status date when processing status changes
        if self.pk:
            original = Lead.objects.get(pk=self.pk)
            if original.processing_status != self.processing_status:
                self.processing_status_date = timezone.now()
        
        super().save(*args, **kwargs)

    def update_processing_status(self, status, executive=None, notes=''):
        """Helper method to update processing status with proper tracking"""
        self.processing_status = status
        self.processing_status_date = timezone.now()
        
        if executive and executive.role == 'PROCESSING':
            self.processing_executive = executive
        
        if notes:
            self.processing_notes = notes
        
        self.save()

    def get_processing_timeline(self):
        """Returns a queryset of processing status changes"""
        return self.processing_updates.all().order_by('-timestamp')

    @property
    def is_forwardable(self):
        """Check if lead can be forwarded to processing"""
        return (self.status == 'REGISTERED' and 
                self.processing_status in ['PENDING', 'REJECTED'])

    @property
    def is_acceptable(self):
        """Check if processing executive can accept this lead"""
        return self.processing_status == 'FORWARDED'

    @property
    def is_completable(self):
        """Check if processing can be marked as complete"""
        return (self.processing_status == 'PROCESSING' and 
                self.processing_executive is not None)


class ProcessingUpdate(models.Model):
    """Model to track processing status changes"""
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE, related_name='processing_updates')
    status = models.CharField(max_length=20, choices=Lead.PROCESSING_STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.lead} - {self.get_status_display()} at {self.timestamp}"


class RemarkHistory(models.Model):
    """History of remarks edits for a lead"""
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE,related_name='remark_history')
    previous_remarks = models.TextField(blank=True, null=True)
    new_remarks = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"Remarks changed for {self.lead} at {self.changed_at}"