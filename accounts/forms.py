from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import (
    User,
    BloodRequest,
    DonorProfile,
    BloodInventory,
)


class RegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'password1',
            'password2',
        )


class BloodRequestForm(forms.ModelForm):

    class Meta:
        model = BloodRequest

        fields = [
            'patient_name',
            'blood_group',
            'units_required',
            'hospital_name',
            'location',
            'contact_number',
            'urgency',
            'additional_message',
        ]

        widgets = {
            'additional_message': forms.Textarea(
                attrs={'rows': 4},
            ),
        }


class DonorProfileForm(forms.ModelForm):

    class Meta:
        model = DonorProfile

        fields = [
            'blood_group',
            'phone_number',
            'location',
            'is_available',
            'last_donation_date',
        ]

        widgets = {
            'last_donation_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
        }


class BloodInventoryForm(forms.ModelForm):

    class Meta:
        model = BloodInventory

        fields = [
            'blood_group',
            'available_units',
        ]

        widgets = {
            'available_units': forms.NumberInput(
                attrs={
                    'min': 0,
                    'placeholder': 'Enter available units',
                }
            ),
        }