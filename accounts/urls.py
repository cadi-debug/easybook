from django.urls import path
from .views import login_user, index, signup, check_availability, logout_user, get_paid
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('', index, name='home'),
    path('signup/', signup, name='signup'),
    path('check_availability/', check_availability, name='check_availability'),
    path('my_reservations/', views.my_reservations, name='my_reservations'),
    path('cancel_reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('get-paid/<int:reservation_id>/', views.get_paid, name='get_paid'),
]
