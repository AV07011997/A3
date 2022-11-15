from django.db import models
from django.contrib.auth.models import User


class Pan(models.Model):
    name = models.CharField(max_length=255, blank=True)
    relative_name = models.CharField(max_length=255, blank=True)
    dob = models.DateField(blank=True, null=True)
    pan_number = models.CharField(max_length=150, blank=True)
    image_name = models.CharField(max_length=255, blank=True)
    image_data = models.BinaryField(blank=False)
    deal_id = models.CharField(max_length=255, blank=True)
    customer_id = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="pan_created_by")
    creation_time = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="pan_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True)
