from django.urls import path
from .views import search_flights, book_flight, download_ticket

app_name = "fly"

urlpatterns = [
    path('search/', search_flights, name='search_flights'),
    path('book/<int:flight_id>/', book_flight, name='book_flight'),
    path('reservation/<int:reservation_id>/download/', download_ticket, name='download_ticket'),
]
