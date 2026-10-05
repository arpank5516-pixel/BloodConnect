from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    BloodRequest,
    DonorProfile,
    RequestVerification,
    HospitalProfile,
    BloodBankProfile,
    DonorResponse,
    Notification,
    BloodInventory,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            'BloodConnect Information',
            {
                'fields': ('role',)
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'BloodConnect Information',
            {
                'fields': ('role',)
            }
        ),
    )


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):

    list_display = (
        'patient_name',
        'blood_group',
        'units_required',
        'hospital_name',
        'urgency',
        'status',
        'created_at',
    )

    list_filter = (
        'blood_group',
        'urgency',
        'status',
    )

    search_fields = (
        'patient_name',
        'hospital_name',
        'location',
    )


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):

    list_display = (
        'donor',
        'blood_group',
        'phone_number',
        'location',
        'is_available',
        'last_donation_date',
    )

    list_filter = (
        'blood_group',
        'is_available',
    )

    search_fields = (
        'donor__username',
        'phone_number',
        'location',
    )


@admin.register(RequestVerification)
class RequestVerificationAdmin(admin.ModelAdmin):

    list_display = (
        'blood_request',
        'status',
        'verified_by',
        'created_at',
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'blood_request__patient_name',
    )


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):

    list_display = (
        'hospital_name',
        'hospital_staff',
        'city',
        'contact_number',
        'verification_status',
        'created_at',
    )

    list_filter = (
        'verification_status',
        'city',
    )

    search_fields = (
        'hospital_name',
        'city',
        'hospital_staff__username',
    )


@admin.register(BloodBankProfile)
class BloodBankProfileAdmin(admin.ModelAdmin):

    list_display = (
        'blood_bank_name',
        'blood_bank_staff',
        'registration_number',
        'city',
        'contact_number',
        'verification_status',
        'created_at',
    )

    list_filter = (
        'verification_status',
        'city',
    )

    search_fields = (
        'blood_bank_name',
        'registration_number',
        'city',
        'blood_bank_staff__username',
    )


@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):

    list_display = (
        'donor',
        'blood_request',
        'response',
        'created_at',
    )

    list_filter = (
        'response',
    )

    search_fields = (
        'donor__donor__username',
        'blood_request__patient_name',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'recipient',
        'notification_type',
        'title',
        'is_read',
        'created_at',
    )

    list_filter = (
        'notification_type',
        'is_read',
    )

    search_fields = (
        'recipient__username',
        'title',
        'message',
    )


@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):

    list_display = (
        'blood_bank',
        'blood_group',
        'available_units',
        'last_updated',
    )

    list_filter = (
        'blood_group',
        'blood_bank',
    )

    search_fields = (
        'blood_bank__blood_bank_name',
        'blood_group',
    )