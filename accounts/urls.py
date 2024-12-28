from django.urls import path
from .views import unified_register_view, verify_email_view, success_view, users_overview_view, logout_view, upload_property_owner_picture, upload_client_picture, list_clients_view, admin_agent_list_view, admin_client_list_view, admin_owner_list_view, owner_update_view

from .api_views import login_api_view

from . import views

from . import api_views

urlpatterns = [
    path('register/', unified_register_view, name='register'),
    path('verify-email/', verify_email_view, name='verify_email'),
    path('success/', success_view, name='success'),
    path('resend-code/', views.resend_verification_code_view, name='resend_code'),
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('owner-dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('client-dashboard/', views.client_dashboard, name='client_dashboard'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('confirm-reset/', views.confirm_reset_view, name='confirm_reset'),
    path('users-overview/', users_overview_view, name='users_overview'),
    path('logout/', logout_view, name='logout'),
    path('delete-user/<int:user_id>/', views.delete_user_view, name='delete_user_view'),
    path('toggle-is-allowed/<int:user_id>/', views.toggle_is_allowed_view, name='toggle_is_allowed'),
    path('delete-user/<int:user_id>/', views.delete_user_confirmation_view, name='delete_user'),
    path('owner/details/', views.owner_details_view, name='owner_details'),
    path('property-owner/upload-picture/', upload_property_owner_picture, name='upload_property_owner_picture'),
    path('client/upload-picture/', upload_client_picture, name='upload_client_picture'),
    path("customer/details/", views.customer_details_view, name="customer_details"),
    path('client/update/', views.update_client_details, name='update_client_details'),
    path('admin/client-list/', list_clients_view, name='list_clients'),
    path('admin/agents/', admin_agent_list_view, name='admin_agent_list'),
    path('admin/clients/list/', admin_client_list_view, name='admin_client_list'),
    path('owners/', admin_owner_list_view, name='admin_owner_list'),
    path('owner/update/', owner_update_view, name='owner_update'),
    path('api/login/', login_api_view, name='login_api'),
    path('api/login/', views.login_json_view, name='login_json'),
    path('api/admin_dashboard/', api_views.admin_dashboard_api, name='admin_dashboard_api'),
]
