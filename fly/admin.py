from django.contrib import admin
from .models import Flight, Airport, Airline, Reservation

admin.site.register(Flight)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Reservation)
