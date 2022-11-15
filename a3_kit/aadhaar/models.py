from django.db import models
from django.contrib.auth.models import User


class Aadhaar(models.Model):
    name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    yob = models.CharField(max_length=50, blank=True)
    gname = models.CharField(max_length=255, blank=True)
    house = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255, blank=True)
    lm = models.CharField(max_length=255, blank=True)
    vtc = models.CharField(max_length=255, blank=True)
    po = models.CharField(max_length=255, blank=True)
    dist = models.CharField(max_length=255, blank=True)
    subdist = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    pc = models.CharField(max_length=255, blank=True)
    dob = models.DateField(blank=True, null=True)
    uid = models.CharField(max_length=255, blank=True)
    image_data = models.BinaryField(blank=False)
    image_name = models.CharField(max_length=255, blank=True)
    deal_id = models.CharField(max_length=255, blank=True)
    customer_id = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="aadhaar_created_by")
    creation_time = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="aadhaar_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True)
