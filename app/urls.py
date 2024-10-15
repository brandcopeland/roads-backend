from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('roads/<int:road_id>/', road_details, name="road_details"),
    path('roads/<int:road_id>/add_to_payment/', add_road_to_draft_payment, name="add_road_to_draft_payment"),
    path('payments/<int:payment_id>/delete/', delete_payment, name="delete_payment"),
    path('payments/<int:payment_id>/', payment)
]
