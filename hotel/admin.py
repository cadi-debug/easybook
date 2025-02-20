from django.contrib import admin
from .models import Room, Rating, Reservation, Hotel, HotelImage, RoomType

admin.site.register(Hotel)
admin.site.register(HotelImage)
admin.site.register(Room)
admin.site.register(RoomType)
admin.site.register(Reservation)
