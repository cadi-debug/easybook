from django.urls import path
from django.views.generic import TemplateView
#from .views import get_paid
from .views import HotelView, HotelDetail, search_hotels

app_name = 'hotel'
urlpatterns = [
    path('hotels/', HotelView.as_view(), name='hotels'),
    path('hotel-detail/<int:pk>/', HotelDetail.as_view(), name='detail'),
    path('search-hotels/', search_hotels, name='search_hotel'),

    path('success/', TemplateView.as_view(template_name='payment/success.html'), name='payment_success'),
    path('notify/', TemplateView.as_view(template_name='payment/notify.html'), name='payment_notify'),
]
