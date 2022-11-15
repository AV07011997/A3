from django.db import models
from django.contrib.auth.models import User


class Bank(models.Model):
    bank_name = models.CharField(max_length=255, blank=False)
    txn_date = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    cheque_number = models.CharField(max_length=255, blank=True, null=True)
    debit = models.FloatField(blank=True, null=True)
    credit = models.FloatField(blank=True, null=True)
    balance = models.FloatField(blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=255, blank=True, null=True)
    deal_id = models.CharField(max_length=255, blank=True)
    customer_id = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="bank_created_by")
    creation_time = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="bank_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True)
    mode = models.CharField(max_length=255, blank=True, null=True)
    sub_mode = models.CharField(max_length=255, blank=True, null=True)
    entity = models.CharField(max_length=255, blank=True, null=True)
    entity_bank = models.CharField(max_length=255, blank=True, null=True)
    source_of_trans = models.CharField(max_length=255, blank=255, null=True)
    transaction_type = models.CharField(max_length=255, blank=255, null=True)
    image_name = models.CharField(max_length=255, blank=True)


class Bank_master(models.Model):
    bank_id = models.CharField(primary_key=True, max_length=255)
    bank_code = models.CharField(unique=True, max_length=255, blank=True)
    bank_name = models.CharField(unique=True, max_length=255, blank=True)
    bank_micr_code = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="bank_master_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="bank_master_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.bank_name)