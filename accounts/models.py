from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ('requester', 'Requester'),
        ('donor', 'Donor'),
        ('hospital', 'Hospital Staff'),
        ('blood_bank', 'Blood Bank Staff'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='requester'
    )

    def __str__(self):
        return self.username


class HospitalProfile(models.Model):

    VERIFICATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    hospital_staff = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='hospital_profile'
    )

    hospital_name = models.CharField(
        max_length=200
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    contact_number = models.CharField(
        max_length=15
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.hospital_name} - {self.verification_status}"


class BloodRequest(models.Model):

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    URGENCY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Emergency', 'Emergency'),
    ]

    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Verification Pending', 'Verification Pending'),
        ('Verified', 'Verified'),
        ('Broadcasted', 'Broadcasted'),
        ('Coordinating', 'Coordinating'),
        ('Closed', 'Closed'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
        ('Expired', 'Expired'),
    ]

    requester = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )

    patient_name = models.CharField(
        max_length=200
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )

    units_required = models.PositiveIntegerField(
        default=1
    )

    hospital = models.ForeignKey(
        'HospitalProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blood_requests'
    )

    hospital_name = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=200
    )

    contact_number = models.CharField(
        max_length=15
    )

    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default='Normal'
    )

    additional_message = models.TextField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Draft'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group} - {self.status}"


class DonorProfile(models.Model):

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    donor = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='donor_profile'
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )

    phone_number = models.CharField(
        max_length=15
    )

    location = models.CharField(
        max_length=200
    )

    is_available = models.BooleanField(
        default=True
    )

    last_donation_date = models.DateField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.donor.username} - {self.blood_group}"


class RequestVerification(models.Model):

    VERIFICATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    blood_request = models.OneToOneField(
        'BloodRequest',
        on_delete=models.CASCADE,
        related_name='verification'
    )

    verified_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_requests'
    )

    status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='Pending'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.blood_request.patient_name} - {self.status}"


class DonorResponse(models.Model):

    RESPONSE_CHOICES = [
        ('Accepted', 'Accepted'),
        ('Declined', 'Declined'),
    ]

    donor = models.ForeignKey(
        'DonorProfile',
        on_delete=models.CASCADE,
        related_name='responses'
    )

    blood_request = models.ForeignKey(
        'BloodRequest',
        on_delete=models.CASCADE,
        related_name='donor_responses'
    )

    response = models.CharField(
        max_length=20,
        choices=RESPONSE_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ('donor', 'blood_request')

    def __str__(self):
        return f"{self.donor.donor.username} - {self.blood_request.patient_name} - {self.response}"


class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ('General', 'General'),
        ('Blood Request', 'Blood Request'),
        ('Emergency', 'Emergency'),
        ('Donor Response', 'Donor Response'),
    ]

    recipient = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='General'
    )

    blood_request = models.ForeignKey(
        'BloodRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


class BloodBankProfile(models.Model):

    VERIFICATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    blood_bank_staff = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='blood_bank_profile'
    )

    blood_bank_name = models.CharField(
        max_length=200
    )

    registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    contact_number = models.CharField(
        max_length=15
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.blood_bank_name} - {self.verification_status}"


class BloodInventory(models.Model):

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    blood_bank = models.ForeignKey(
        'BloodBankProfile',
        on_delete=models.CASCADE,
        related_name='inventory'
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )

    available_units = models.PositiveIntegerField(
        default=0
    )

    last_updated = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ('blood_bank', 'blood_group')

    def __str__(self):
        return f"{self.blood_bank.blood_bank_name} - {self.blood_group} - {self.available_units} units"