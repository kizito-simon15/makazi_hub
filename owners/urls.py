from django.urls import path
from .views import (
    create_house_step1_view,
    create_house_step2_view,
    create_house_step3_view,
    create_house_step4_view,
    create_house_step5_view,
    house_list_view,
    house_details_view,
    delete_house_view,
    delete_rooms_view,
    create_booking_rule_view,
    delete_booking_rule_view,
    agent_dashboard_view,
    send_message_view,
    agent_conversations_view,
    promotions_overview_view,
    agent_only_details_view,
    agent_houses_overview_view
)

from . import views

urlpatterns = [
    path('browse/houses/in/public', views.browse_houses_public_view, name='browse_houses_public'),
    path('owners/houses/list/', house_list_view, name='house_list'),
    path('register_error/', views.register_error_view, name='register_error'),
    path('house/<int:house_id>/public/details/', views.house_full_details_view, name='house_full_details'),
    path('owners/create/house/step1/', create_house_step1_view, name='create_house_step1'),
    path('owners/create/house/step1/<int:house_id>/', create_house_step1_view, name='create_house_step1_with_id'),
    path("owners/create/house/step2/<int:house_id>/", create_house_step2_view, name="create_house_step2"),
    path("owners/create/house/step3/<int:house_id>/", create_house_step3_view, name="create_house_step3"),
    path("owners/create/house/step4/<int:house_id>/", create_house_step4_view, name="create_house_step4"),
    path('house/<int:house_id>/create-step5/', create_house_step5_view, name='create_house_step5'),
    path("house/<int:house_id>/details/", house_details_view, name="house_details"),
    path("delete/house/<int:house_id>/", delete_house_view, name="delete_house"),
    path("delete/rooms/<int:house_id>/", delete_rooms_view, name="delete_rooms"),
    path('browse-houses/', views.browse_houses_view, name='browse_houses'),
    path('client/house/<int:house_id>/', views.client_house_details_view, name='client_house_details'),
    path('agents/create/', views.create_agent_view, name='create_agent'),
    path('agent/<int:agent_id>/edit/', views.create_agent_view, name='edit_agent'),
    path('agents/listings/', views.agent_list_view, name='agent_list'),
    path('agents/<int:agent_id>/update-verification/', views.update_agent_verification, name='update_agent_verification'),
    path('agents/<int:agent_id>/delete/', views.delete_agent_view, name='delete_agent'),
    path('create-booking-rule/', create_booking_rule_view, name='create_booking_rule'),
    path('booking/rules/list/', views.booking_rules_list_view, name='booking_rules_list'),
    path('create-booking-rule/<int:house_id>/', views.create_booking_rule_view, name='create_or_update_booking_rule'),
    path('delete-booking-rule/<int:rule_id>/', delete_booking_rule_view, name='delete_booking_rule'),
    path("house/<int:house_id>/like-toggle/", views.toggle_house_like, name="toggle_house_like"),
    path("liked-houses/", views.liked_houses_view, name="liked_houses"),
    path("comment/update/", views.update_comment, name="update_comment"),
    path("comment/delete/", views.delete_comment, name="delete_comment"),
    path("comment/add/", views.add_comment, name="add_comment"),
    path("comment/add/", views.add_client_comment, name="add_client_comment"),
    path("comment/edit/", views.edit_client_comment, name="edit_client_comment"),
    path("comment/delete/", views.delete_client_comment, name="delete_client_comment"),
    path('agent/dashboard/', agent_dashboard_view, name='agent_dashboard'),
    path('house/<int:house_id>/agent/<int:agent_id>/send_message/', send_message_view, name='send_message'),
    path('agent/conversations/', agent_conversations_view, name='agent_conversations'),
    path('agent/chat/<int:client_id>/', views.agent_chat_view, name='agent_chat'),
    path('client/agents/list/', views.client_agents_list_view, name='client_agents_list'),
    path('promotion/step1/', views.promotion_step1_view, name='promotion_step1'),
    path('promotion/step2/', views.promotion_step2_view, name='promotion_step2'),
    path('promotions/overview/', promotions_overview_view, name='promotions_overview'),
    path('agent/only/details/', agent_only_details_view, name='agent_only_details'),
    path('agent/houses-overview/', agent_houses_overview_view, name='agent_houses_overview'),
    path('ajax/load-districts/', views.load_districts, name='load_districts'),
    path('ajax/load-wards/', views.load_wards, name='load_wards'),
    path('ajax/load-streets/', views.load_streets, name='load_streets'),
    path('room/<int:room_id>/', views.room_details_view, name='room_details'),
    # Updating
    path("owners/update/house/step2/<int:house_id>/", views.update_house_step2_view, name="update_house_step2"),
    path("owners/update/house/step3/<int:house_id>/", views.update_house_step3_view, name="update_house_step3"),
    path("owners/update/house/step4/<int:house_id>/", views.update_house_step4_view, name="update_house_step4"),

    # House additional features
    path(
        'houses/<int:house_id>/step1-features/', 
        views.step1_additional_features_view, 
        name='step1_features'
    ),
    path(
        'houses/<int:house_id>/step2-features/',
        views.step2_additional_features_view,
        name='step2_features'
    ),

    path(
        'houses/<int:house_id>/rent-as-whole/',
        views.house_rent_as_whole_view,
        name='house_rent_as_whole'
    ),

    path(
        'houses/<int:house_id>/update-step1-features/',
        views.update_house_step1_features,
        name='update_house_step1_features'
    ),

    path(
        'houses/<int:house_id>/update-step3-features/',
        views.update_house_step3_features,
        name='update_house_step3_features'
    ),

    path(
        'houses/<int:house_id>/update-rent-as-whole/',
        views.update_house_rent_as_whole,
        name='update_house_rent_as_whole'
    ),

    path(
        'houses/<int:house_id>/create-update/',
        views.create_house_update,
        name='create_house_update'
    ),

    path(
        'houses/<int:house_id>/updates/',
        views.house_updates_view,
        name='house_updates'
    ),
]
