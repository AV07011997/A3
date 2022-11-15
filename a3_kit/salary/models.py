from django.db import models
from django.contrib.auth.models import User
from mysite.models import Customer_details


class Salary(models.Model):
    deal_id = models.CharField(max_length=255, blank=False)
    customer = models.ForeignKey(Customer_details, blank=False, null=True, on_delete=models.SET_NULL)
    month1 = models.CharField(max_length=255, blank=True)
    month2 = models.CharField(max_length=255, blank=True)
    month3 = models.CharField(max_length=255, blank=True)
    month4 = models.CharField(max_length=255, blank=True)
    month5 = models.CharField(max_length=255, blank=True)
    month6 = models.CharField(max_length=255, blank=True)
    month7 = models.CharField(max_length=255, blank=True)
    sal_type = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="salary_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="salary_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.deal_id)