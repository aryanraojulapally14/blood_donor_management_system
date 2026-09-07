
from django.urls import path
from . import views

urlpatterns = [
path('', views.home, name='home'),
path('register/', views.register_donor, name='register'),
path('login/', views.login_view, name='login'),
path('dashboard/', views.dashboard, name='dashboard'),
path('search/', views.search, name='search'),
path('create-request/', views.create_request, name='create_request'),
path('view-requests/', views.view_requests, name='view_requests'),
path('register-hospital/', views.register_hospital, name='register_hospital'),
path('logout/', views.user_logout, name='logout'),
path('profile/', views.profile, name='profile'),
path('update-donation/', views.update_donation, name='update_donation'),
path('donate/', views.donate_today, name='donate'),
path('contact/<int:donor_id>/', views.contact_donor, name='contact_donor'),
path('request-history/', views.request_history, name='request_history'),
path('my-donations/', views.donor_history, name='donor_history'),
path('donor-requests/', views.donor_requests, name='donor_requests'),
path('mark-donated/<int:request_id>/', views.mark_donated, name='mark_donated'),
path('confirm-request/<int:request_id>/', views.confirm_request, name='confirm_request'),
]
