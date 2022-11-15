from django.db import models
from django.contrib.auth.models import User
from bank.models import Bank_master


class Country_master(models.Model):
    country_id = models.CharField(primary_key=True, max_length=255)
    country_name = models.CharField(unique=True, max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="country_master_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="country_master_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.country_name)


class State_master(models.Model):
    state_id = models.CharField(primary_key=True, max_length=255)
    state_desc = models.CharField(unique=True, max_length=255, blank=True)
    country = models.ForeignKey(Country_master, blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="state_master_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="state_master_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.state_desc)


class District_master(models.Model):
    district_id = models.CharField(primary_key=True, max_length=255)
    district_desc = models.CharField(unique=True, max_length=255, blank=True)
    state = models.ForeignKey(State_master, blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="district_master_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="district_master_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.district_desc)


class Customer_details(models.Model):
    customer_id = models.CharField(primary_key=True, max_length=255)
    customer_name = models.CharField(max_length=255, blank=True)
    customer_fname = models.CharField(max_length=255, blank=True)
    customer_mname = models.CharField(max_length=255, blank=True)
    customer_lname = models.CharField(max_length=255, blank=True)
    customer_type = models.CharField(max_length=255, blank=True)
    customer_dob = models.DateField(null=True, blank=True)
    customer_constitution = models.CharField(max_length=255, blank=True)
    customer_voter_id = models.CharField(max_length=255, blank=True)
    customer_uid = models.CharField(max_length=255, blank=True)
    customer_pan = models.CharField(max_length=255, blank=True)
    customer_gender = models.CharField(max_length=255, blank=True)
    customer_marital_status = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="customer_details_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="customer_details_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.customer_name)


class Customer_address(models.Model):
    customer = models.OneToOneField(Customer_details, primary_key=True, on_delete=models.CASCADE)
    address_type = models.CharField(max_length=255, blank=True)
    bptype = models.CharField(max_length=255, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    address_line3 = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(Country_master, blank=True, null=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State_master, blank=True, null=True, on_delete=models.SET_NULL)
    district = models.ForeignKey(District_master, blank=True, null=True, on_delete=models.SET_NULL)
    pin_code = models.CharField(max_length=255, blank=True)
    primary_phone = models.CharField(max_length=255, blank=True)
    communication_address = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="customer_address_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="customer_address_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.customer)


class Los_details(models.Model):
    customer = models.ForeignKey(Customer_details, null=True, blank=True, on_delete=models.SET_NULL)
    deal_id = models.CharField(max_length=255, blank=True)
    loan_id = models.CharField(max_length=255, blank=True)
    deal_customer_role_type = models.CharField(max_length=255, blank=True)
    deal_customer_type = models.CharField(max_length=255, blank=True)
    existing_customer = models.CharField(max_length=255, blank=True)
    bank_name = models.ForeignKey(Bank_master, null=True, blank=True, on_delete=models.SET_NULL)
    bank_branch = models.CharField(max_length=255, blank=True)
    account_no = models.CharField(max_length=255, blank=True)
    account_type = models.CharField(max_length=255, blank=True)
    guarantee_amount = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="los_details_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="los_details_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.customer)


class Document_type_master(models.Model):
    document_id = models.CharField(primary_key=True, max_length=255)
    document_name = models.CharField(unique=True, max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="document_type_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="document_type_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.document_name)


class Processed_document_details(models.Model):
    deal_id = models.CharField(max_length=255, blank=False)
    customer = models.ForeignKey(Customer_details, blank=True, null=True, on_delete=models.SET_NULL)
    loan_id = loan_id = models.CharField(max_length=255, blank=True)
    document = models.ForeignKey(Document_type_master, blank=True, null=True, on_delete=models.SET_NULL)
    uploaded_document_path = models.CharField(max_length=255, blank=True)
    upload_status = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="processed_document_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="processed_document_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.deal_id)


class Unprocessed_document_details(models.Model):
    deal_id = models.CharField(max_length=255, blank=False)
    customer = models.ForeignKey(Customer_details, blank=True, null=True, on_delete=models.SET_NULL)
    loan_id = loan_id = models.CharField(max_length=255, blank=True)
    document = models.ForeignKey(Document_type_master, blank=True, null=True, on_delete=models.SET_NULL)
    uploaded_document_path = models.CharField(max_length=255, blank=True)
    upload_status = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="unprocessed_document_created_by")
    creation_time = models.DateTimeField(auto_now_add=True, null=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="unprocessed_document_last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.deal_id)


class Uploaded_itrv_form16_form26as_details(models.Model):
    deal_id = models.CharField(max_length=255, blank=False)
    customer_id = models.CharField(max_length=255, blank=False)
    year = models.CharField(max_length=255, blank=False)
    document_type = models.CharField(max_length=255, blank=False)
    file_name = models.CharField(max_length=255, blank=False)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="created_by")
    creation_time = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="last_modified_by")
    last_modification_time = models.DateTimeField(auto_now=True)

        
class Uploaded_bank_statements_details(models.Model):
    deal_id = models.CharField(max_length=255, blank=False)
    customer_id = models.CharField(max_length=255, blank=False)
    action_type = models.CharField(max_length=255, blank=False)
    bank_index = models.CharField(max_length=255, blank=False)
    bank_id = models.CharField(max_length=255, blank=False)
    bank_name = models.CharField(max_length=255, blank=True)
    file_name = models.CharField(max_length=255, blank=False)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="created_by_user")
    creation_time = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="last_modified_by_user")
    last_modification_time = models.DateTimeField(auto_now=True)
