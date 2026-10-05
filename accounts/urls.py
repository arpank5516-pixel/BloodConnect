from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect

from . import views


def logout_view(request):
    logout(request)
    return redirect('login')


def accounts_home(request):
    return redirect('login')


urlpatterns = [

    path(
        '',
        accounts_home,
        name='accounts_home'
    ),

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html'
        ),
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),

    path(
        'profile/',
        views.profile,
        name='profile'
    ),

    path(
        'home/',
        views.home,
        name='home'
    ),

    path(
        'find-donor/',
        views.find_donor,
        name='find_donor'
    ),

    path(
        'request-blood/',
        views.create_blood_request,
        name='create_blood_request'
    ),

    path(
        'my-blood-requests/',
        views.my_blood_requests,
        name='my_blood_requests'
    ),

    path(
        'donor-profile/',
        views.donor_profile,
        name='donor_profile'
    ),

    path(
        'donor/requests/',
        views.donor_requests,
        name='donor_requests'
    ),

    path(
        'donor/accept/<int:request_id>/',
        views.accept_blood_request,
        name='accept_blood_request'
    ),

    path(
        'donor/decline/<int:request_id>/',
        views.decline_blood_request,
        name='decline_blood_request'
    ),

    path(
        'emergency-broadcast/<int:request_id>/',
        views.emergency_broadcast,
        name='emergency_broadcast'
    ),

    path(
        'notification/read/<int:notification_id>/',
        views.mark_notification_read,
        name='mark_notification_read'
    ),

    path(
        'hospital-dashboard/',
        views.hospital_dashboard,
        name='hospital_dashboard'
    ),

    path(
        'hospital/verify-request/<int:request_id>/',
        views.verify_blood_request,
        name='verify_blood_request'
    ),

    path(
        'hospital/start-coordination/<int:request_id>/',
        views.start_coordination,
        name='start_coordination'
    ),

    path(
        'hospital/reject-request/<int:request_id>/',
        views.reject_blood_request,
        name='reject_blood_request'
    ),

    path(
        'hospital/close-request/<int:request_id>/',
        views.close_blood_request,
        name='close_blood_request'
    ),

    path(
        'blood-bank-dashboard/',
        views.blood_bank_dashboard,
        name='blood_bank_dashboard'
    ),

    path(
        'blood-bank-inventory/',
        views.blood_bank_inventory,
        name='blood_bank_inventory'
    ),
]