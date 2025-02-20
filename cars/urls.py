from django.urls import path

from cars.views import reserve_car, confirmation

app_name = 'cars'

urlpatterns = [
    path('cars-reservation/', reserve_car, name='cars_reservation'),
    path('confirmation/', confirmation, name='confirmation'),
]