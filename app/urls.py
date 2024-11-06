from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/roads/', search_roads),  # GET
    path('api/roads/<int:road_id>/', get_road_by_id),  # GET
    path('api/roads/<int:road_id>/update/', update_road),  # PUT
    path('api/roads/<int:road_id>/update_image/', update_road_image),  # POST
    path('api/roads/<int:road_id>/delete/', delete_road),  # DELETE
    path('api/roads/create/', create_road),  # POST
    path('api/roads/<int:road_id>/add_to_payment/', add_road_to_payment),  # POST

    # Набор методов для заявок
    path('api/payments/', search_payments),  # GET
    path('api/payments/<int:payment_id>/', get_payment_by_id),  # GET
    path('api/payments/<int:payment_id>/update/', update_payment),  # PUT
    path('api/payments/<int:payment_id>/update_status_user/', update_status_user),  # PUT
    path('api/payments/<int:payment_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/payments/<int:payment_id>/delete/', delete_payment),  # DELETE

    # Набор методов для м-м
    path('api/payments/<int:payment_id>/roads/<int:road_id>/', get_road_payment),  # GET
    path('api/payments/<int:payment_id>/update_road/<int:road_id>/', update_road_in_payment),  # PUT
    path('api/payments/<int:payment_id>/delete_road/<int:road_id>/', delete_road_from_payment),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
