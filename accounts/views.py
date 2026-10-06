from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    BloodInventoryForm,
    BloodRequestForm,
    DonorProfileForm,
    RegistrationForm,
)

from .models import (
    BloodBankProfile,
    BloodInventory,
    BloodRequest,
    DonorProfile,
    DonorResponse,
    HospitalProfile,
    Notification,
    RequestVerification,
    User,
)


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = RegistrationForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Registration successful. Please login.'
            )

            return redirect('login')

    else:
        form = RegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {
            'form': form
        }
    )


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(
        request,
        'accounts/login.html'
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required
def user_logout(request):

    logout(request)

    return redirect('login')


# =========================================================
# HOME / DASHBOARD
# =========================================================

@login_required
def home(request):

    # Donor ke liye direct matching blood requests
    if request.user.role == 'donor':
        return redirect('donor_requests')

    total_requests = BloodRequest.objects.filter(
        requester=request.user
    ).count()

    pending_requests = BloodRequest.objects.filter(
        requester=request.user,
        status__in=[
            'Draft',
            'Submitted',
            'Verification Pending'
        ]
    ).count()

    verified_requests = BloodRequest.objects.filter(
        requester=request.user,
        status='Verified'
    ).count()

    completed_requests = BloodRequest.objects.filter(
        requester=request.user,
        status='Closed'
    ).count()

    recent_requests = BloodRequest.objects.filter(
        requester=request.user
    ).order_by(
        '-created_at'
    )[:5]

    return render(
        request,
        'accounts/home.html',
        {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'verified_requests': verified_requests,
            'completed_requests': completed_requests,
            'recent_requests': recent_requests,
        }
    )


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile(request):

    # Agar user donor hai,
    # to direct Donor Profile form par bhejo
    if request.user.role == 'donor':
        return redirect('donor_profile')

    donor_profile = DonorProfile.objects.filter(
        donor=request.user
    ).first()

    return render(
        request,
        'accounts/profile.html',
        {
            'donor_profile': donor_profile,
        }
    )


# =========================================================
# FIND DONOR
# =========================================================

@login_required
def find_donor(request):

    donors = DonorProfile.objects.filter(
        is_available=True,
        donor__role='donor'
    ).select_related(
        'donor'
    )

    blood_group = request.GET.get('blood_group')
    location = request.GET.get('location')

    if blood_group:

        donors = donors.filter(
            blood_group=blood_group
        )

    if location:

        donors = donors.filter(
            location__icontains=location
        )

    return render(
        request,
        'accounts/find_donor.html',
        {
            'donors': donors
        }
    )


# =========================================================
# REQUEST BLOOD
# =========================================================

@login_required
def request_blood(request):

    if request.method == 'POST':

        form = BloodRequestForm(
            request.POST
        )

        if form.is_valid():

            blood_request = form.save(
                commit=False
            )

            blood_request.requester = request.user

            # Direct donor workflow
            # Hospital verification is not required
            blood_request.status = 'Verified'

            # Hospital name ke basis par
            # HospitalProfile find karo
            hospital_name = form.cleaned_data.get(
                'hospital_name'
            )

            hospital_profile = HospitalProfile.objects.filter(
                hospital_name__iexact=hospital_name
            ).first()

            if hospital_profile:

                blood_request.hospital = hospital_profile

            blood_request.save()

            # Request automatically verified
            RequestVerification.objects.create(
                blood_request=blood_request,
                status='Verified'
            )

            messages.success(
                request,
                'Blood request submitted successfully.'
            )

            return redirect(
                'my_blood_requests'
            )

    else:

        form = BloodRequestForm()

    return render(
        request,
        'accounts/request_blood.html',
        {
            'form': form
        }
    )


# =========================================================
# COMPATIBILITY URL
# =========================================================

@login_required
def create_blood_request(request):

    return request_blood(request)


# =========================================================
# MY BLOOD REQUESTS
# =========================================================

@login_required
def my_blood_requests(request):

    blood_requests = BloodRequest.objects.filter(
        requester=request.user
    ).select_related(
        'hospital'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'accounts/my_blood_requests.html',
        {
            'blood_requests': blood_requests
        }
    )


# =========================================================
# DONOR PROFILE
# =========================================================

@login_required
def donor_profile(request):

    if request.user.role != 'donor':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    profile = DonorProfile.objects.filter(
        donor=request.user
    ).first()

    if request.method == 'POST':

        form = DonorProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            donor = form.save(
                commit=False
            )

            donor.donor = request.user

            donor.save()

            messages.success(
                request,
                'Donor profile saved successfully.'
            )

            return redirect(
                'donor_profile'
            )

    else:

        form = DonorProfileForm(
            instance=profile
        )

    return render(
        request,
        'accounts/donor_profile.html',
        {
            'form': form,
            'profile': profile,
        }
    )


# =========================================================
# DONOR REQUESTS
# =========================================================

@login_required
def donor_requests(request):

    if request.user.role != 'donor':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    donor_profile = DonorProfile.objects.filter(
        donor=request.user
    ).first()

    if not donor_profile:

        messages.warning(
            request,
            'Please complete your donor profile first.'
        )

        return redirect(
            'donor_profile'
        )

    responded_request_ids = DonorResponse.objects.filter(
        donor=donor_profile
    ).values_list(
        'blood_request_id',
        flat=True
    )

    # Direct matching:
    # Verified requests bhi donor ko dikhenge
    blood_requests = BloodRequest.objects.filter(
        status__in=[
            'Verified',
            'Broadcasted',
            'Coordinating'
        ],
        blood_group=donor_profile.blood_group
    ).exclude(
        id__in=responded_request_ids
    ).select_related(
        'hospital'
    ).order_by(
        '-created_at'
    )

    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by(
        '-created_at'
    )

    unread_notifications = notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        'accounts/donor_requests.html',
        {
            'blood_requests': blood_requests,
            'donor_profile': donor_profile,
            'notifications': notifications,
            'unread_notifications': unread_notifications,
        }
    )


# =========================================================
# DONOR ACCEPT
# =========================================================

@login_required
def donor_accept(request, request_id):

    if request.user.role != 'donor':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id
    )

    donor_profile = get_object_or_404(
        DonorProfile,
        donor=request.user
    )

    DonorResponse.objects.update_or_create(
        donor=donor_profile,
        blood_request=blood_request,
        defaults={
            'response': 'Accepted'
        }
    )
    blood_request.status = 'Coordinating'
    blood_request.save()  

    Notification.objects.create(
        recipient=blood_request.requester,
        title='Donor Accepted Your Request',
        message=(
            f'{request.user.username} has accepted '
            f'the blood request for '
            f'{blood_request.patient_name}.'
        ),
        notification_type='Donor Response',
        blood_request=blood_request
    )

    messages.success(
        request,
        'Blood request accepted successfully.'
    )

    return redirect(
        'donor_requests'
    )


# =========================================================
# COMPATIBILITY URL
# =========================================================

@login_required
def accept_blood_request(request, request_id):

    return donor_accept(
        request,
        request_id
    )


# =========================================================
# DONOR DECLINE
# =========================================================

@login_required
def donor_decline(request, request_id):

    if request.user.role != 'donor':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id
    )

    donor_profile = get_object_or_404(
        DonorProfile,
        donor=request.user
    )

    DonorResponse.objects.update_or_create(
        donor=donor_profile,
        blood_request=blood_request,
        defaults={
            'response': 'Declined'
        }
    )

    messages.info(
        request,
        'Blood request declined.'
    )

    return redirect(
        'donor_requests'
    )


# =========================================================
# COMPATIBILITY URL
# =========================================================

@login_required
def reject_blood_request(request, request_id):

    return donor_decline(
        request,
        request_id
    )


@login_required
def decline_blood_request(request, request_id):

    return donor_decline(
        request,
        request_id
    )


# =========================================================
# EMERGENCY BROADCAST
# =========================================================

@login_required
def emergency_broadcast(request, request_id):

    if request.user.role not in [
        'requester',
        'hospital'
    ]:

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id
    )

    blood_request.status = 'Broadcasted'
    blood_request.urgency = 'Emergency'

    blood_request.save()

    donors = DonorProfile.objects.filter(
        blood_group=blood_request.blood_group,
        is_available=True
    ).select_related(
        'donor'
    )

    for donor in donors:

        Notification.objects.create(
            recipient=donor.donor,
            title='Emergency Blood Request',
            message=(
                f'Emergency blood required: '
                f'{blood_request.blood_group} - '
                f'{blood_request.units_required} units '
                f'for {blood_request.patient_name}.'
            ),
            notification_type='Emergency',
            blood_request=blood_request
        )

    messages.success(
        request,
        'Emergency blood request broadcasted.'
    )

    return redirect(
        'my_blood_requests'
    )


# =========================================================
# NOTIFICATION READ
# =========================================================

@login_required
def mark_notification_read(
    request,
    notification_id
):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save()

    if request.user.role == 'donor':

        return redirect(
            'donor_requests'
        )

    if request.user.role == 'hospital':

        return redirect(
            'hospital_dashboard'
        )

    if request.user.role == 'blood_bank':

        return redirect(
            'blood_bank_dashboard'
        )

    return redirect(
        'home'
    )


# =========================================================
# HOSPITAL DASHBOARD
# =========================================================

@login_required
def hospital_dashboard(request):

    if request.user.role != 'hospital':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    hospital_profile = HospitalProfile.objects.filter(
        hospital_staff=request.user
    ).first()

    blood_requests = BloodRequest.objects.none()

    if hospital_profile:

        blood_requests = BloodRequest.objects.filter(
            hospital=hospital_profile
        ).select_related(
            'requester'
        ).prefetch_related(
            'donor_responses__donor__donor'
        ).order_by(
            '-created_at'
        )

    return render(
        request,
        'accounts/hospital_dashboard.html',
        {
            'hospital_profile': hospital_profile,
            'blood_requests': blood_requests,
        }
    )


# =========================================================
# HOSPITAL START COORDINATION
# =========================================================

@login_required
def hospital_start_coordination(
    request,
    request_id
):

    if request.user.role != 'hospital':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    hospital_profile = get_object_or_404(
        HospitalProfile,
        hospital_staff=request.user
    )

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        hospital=hospital_profile
    )

    if blood_request.status in [
        'Verified',
        'Broadcasted'
    ]:

        blood_request.status = 'Coordinating'

        blood_request.save()

        messages.success(
            request,
            'Request moved to Coordinating.'
        )

    return redirect(
        'hospital_dashboard'
    )


# =========================================================
# HOSPITAL REJECT
# =========================================================

@login_required
def hospital_reject_request(
    request,
    request_id
):

    if request.user.role != 'hospital':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    hospital_profile = get_object_or_404(
        HospitalProfile,
        hospital_staff=request.user
    )

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        hospital=hospital_profile
    )

    if blood_request.status in [
        'Verified',
        'Broadcasted'
    ]:

        blood_request.status = 'Rejected'

        blood_request.save()

        messages.warning(
            request,
            'Blood request rejected.'
        )

    return redirect(
        'hospital_dashboard'
    )


# =========================================================
# HOSPITAL CLOSE REQUEST
# =========================================================

@login_required
def hospital_close_request(
    request,
    request_id
):

    if request.user.role != 'hospital':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    hospital_profile = get_object_or_404(
        HospitalProfile,
        hospital_staff=request.user
    )

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        hospital=hospital_profile
    )

    blood_request.status = 'Closed'

    blood_request.save()

    messages.success(
        request,
        'Blood request closed successfully.'
    )

    return redirect(
        'hospital_dashboard'
    )


# =========================================================
# BLOOD BANK DASHBOARD
# =========================================================

@login_required
def blood_bank_dashboard(request):

    if request.user.role != 'blood_bank':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    blood_bank_profile = None

    try:

        blood_bank_profile = BloodBankProfile.objects.get(
            blood_bank_staff=request.user
        )

    except BloodBankProfile.DoesNotExist:

        pass

    inventory = BloodInventory.objects.none()

    blood_requests = BloodRequest.objects.filter(
        status__in=[
            'Verified',
            'Broadcasted',
            'Coordinating'
        ]
    ).select_related(
        'hospital'
    ).order_by(
        '-created_at'
    )

    stock_data = {}

    if blood_bank_profile:

        inventory = BloodInventory.objects.filter(
            blood_bank=blood_bank_profile
        ).order_by(
            'blood_group'
        )

        for blood_request in blood_requests:

            stock = BloodInventory.objects.filter(
                blood_bank=blood_bank_profile,
                blood_group=blood_request.blood_group
            ).first()

            if stock:

                stock_data[blood_request.id] = (
                    stock.available_units
                )

            else:

                stock_data[blood_request.id] = 0

    return render(
        request,
        'accounts/blood_bank_dashboard.html',
        {
            'blood_bank_profile': blood_bank_profile,
            'inventory': inventory,
            'blood_requests': blood_requests,
            'stock_data': stock_data,
        }
    )


# =========================================================
# BLOOD BANK INVENTORY
# =========================================================

@login_required
def blood_bank_inventory(request):

    if request.user.role != 'blood_bank':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    blood_bank_profile = get_object_or_404(
        BloodBankProfile,
        blood_bank_staff=request.user
    )

    inventory = BloodInventory.objects.filter(
        blood_bank=blood_bank_profile
    ).order_by(
        'blood_group'
    )

    if request.method == 'POST':

        form = BloodInventoryForm(
            request.POST
        )

        if form.is_valid():

            blood_group = form.cleaned_data[
                'blood_group'
            ]

            available_units = form.cleaned_data[
                'available_units'
            ]

            BloodInventory.objects.update_or_create(
                blood_bank=blood_bank_profile,
                blood_group=blood_group,
                defaults={
                    'available_units': available_units
                }
            )

            messages.success(
                request,
                f'{blood_group} stock updated successfully.'
            )

            return redirect(
                'blood_bank_inventory'
            )

    else:

        form = BloodInventoryForm()

    return render(
        request,
        'accounts/blood_bank_inventory.html',
        {
            'form': form,
            'inventory': inventory,
            'blood_bank_profile': blood_bank_profile,
        }
    )


# =========================================================
# START COORDINATION
# =========================================================

@login_required
def start_coordination(request, request_id):

    if request.user.role != 'hospital':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    hospital_profile = get_object_or_404(
        HospitalProfile,
        hospital_staff=request.user
    )

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        hospital=hospital_profile
    )

    if blood_request.status in [
        'Verified',
        'Broadcasted'
    ]:

        blood_request.status = 'Coordinating'

        blood_request.save()

        messages.success(
            request,
            'Request moved to Coordinating.'
        )

    return redirect(
        'hospital_dashboard'
    )


# =========================================================
# CLOSE BLOOD REQUEST
# =========================================================

@login_required
def close_blood_request(request, request_id):

    if request.user.role != 'hospital':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    hospital_profile = get_object_or_404(
        HospitalProfile,
        hospital_staff=request.user
    )

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        hospital=hospital_profile
    )

    if blood_request.status == 'Coordinating':

        blood_request.status = 'Closed'

        blood_request.save()

        messages.success(
            request,
            'Blood request closed successfully.'
        )

    return redirect(
        'hospital_dashboard'
    )


# =========================================================
# VERIFY BLOOD REQUEST
# =========================================================

@login_required
def verify_blood_request(request, request_id):

    if request.user.role != 'hospital':

        messages.error(
            request,
            'Access denied.'
        )

        return redirect('home')

    hospital_profile = get_object_or_404(
        HospitalProfile,
        hospital_staff=request.user
    )

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        hospital=hospital_profile
    )

    if blood_request.status == 'Submitted':

        blood_request.status = 'Verified'

        blood_request.save()

        verification, created = (
            RequestVerification.objects.get_or_create(
                blood_request=blood_request
            )
        )

        verification.status = 'Verified'
        verification.verified_by = request.user
        verification.save()

        messages.success(
            request,
            'Blood request verified successfully.'
        )

    return redirect(
        'hospital_dashboard'
    )