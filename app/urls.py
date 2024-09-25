from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('roads/<int:road_id>/', road),
    path('payments/<int:payment_id>/', payment),
]