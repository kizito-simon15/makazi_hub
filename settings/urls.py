from django.urls import path
from . import views

from .views import HouseLocationCreateView, HouseLocationDetailView, houses_map_view

urlpatterns = [
    path('payments/create/', views.create_payment_view, name='create_payment'),
    path('payments/', views.payments_list_view, name='payments_list'),
    path('payment/update/<int:payment_id>/', views.update_payment_view, name='update_payment'),
    path('payment/delete/<int:payment_id>/', views.delete_payment_view, name='delete_payment'),
    path('create/region/', views.create_region_view, name='create_region'),
    path('regions/list/', views.region_list_view, name='region_list'),
    path('delete/<int:pk>/regions/view/', views.delete_region_view, name='delete_region'),
    path('<int:region_pk>/districts/create/', views.create_district_view, name='create_district'),
    path('<int:region_pk>/districts/<int:district_pk>/wards/create/', views.create_ward_view, name='create_ward'),
    path('<int:region_pk>/districts/<int:district_pk>/wards/<int:ward_pk>/streets/create/', views.create_street_view, name='create_street'),
    path('region/<int:region_pk>/update/', views.update_region_view, name='update_region'),
    path('<int:region_pk>/districts/<int:district_pk>/update/', views.update_district_view, name='update_district'),
    path('<int:region_pk>/districts/<int:district_pk>/wards/<int:ward_pk>/update/', views.update_ward_view, name='update_ward'),
    path('<int:region_pk>/districts/<int:district_pk>/wards/<int:ward_pk>/streets/<int:street_pk>/update/', views.update_street_view, name='update_street'),
    # Deletions
    path('region/<int:region_pk>/delete/', views.delete_region_view, name='delete_region'),
    path('<int:region_pk>/districts/<int:district_pk>/delete/', views.delete_district_view, name='delete_district'),
    path('<int:region_pk>/districts/<int:district_pk>/wards/<int:ward_pk>/delete/', views.delete_ward_view, name='delete_ward'),
    path('<int:region_pk>/districts/<int:district_pk>/wards/<int:ward_pk>/streets/<int:street_pk>/delete/', views.delete_street_view, name='delete_street'),
    # Add other paths like payment_list if needed

    path('houses/<int:house_id>/location/add/', HouseLocationCreateView.as_view(), name='add_house_location'),
    path('houses/<int:house_id>/location/detail/', HouseLocationDetailView.as_view(), name='house_location_detail'),
    path('houses/map/', houses_map_view, name='houses_map_view'),
]

