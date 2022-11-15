from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class bank_customer_month_kpi(models.Model):

	bank_name = models.CharField(max_length=250)
	account_number = models.CharField(max_length=250)
	# from_date = models.DateField()
	# to_date = models.DateField()
