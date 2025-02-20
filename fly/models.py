from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string


def upload_ticket(instance, filename):
    return f"tickets/{instance.user.username}_{get_random_string(8)}.png"


class Airline(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.city}, {self.country})"


class Flight(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name='flights')
    CLASS_CHOICES = [
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('first', 'First Class'),
    ]
    flight_class = models.CharField(max_length=10, choices=CLASS_CHOICES, default='economy')
    flight_number = models.CharField(max_length=10)
    departure_airport = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE)
    arrival_airport = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    departure_city = models.CharField(max_length=200)
    arrival_city = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Flight {self.flight_number}: {self.departure_airport} → {self.arrival_airport}"


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plane_user')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    reserved_on = models.DateTimeField(auto_now_add=True)
    passengers = models.PositiveIntegerField()
    qr_code = models.ImageField(upload_to=upload_ticket, blank=True, null=True)

    def __str__(self):
        return f"Reservation by {self.user} for {self.flight}"

    def generate_qr_code(self):
        import qrcode
        from io import BytesIO
        from django.core.files.base import ContentFile

        qr_data = f"Reservation ID: {self.id}\nFlight: {self.flight}\nUser: {self.user}\nDate: {self.reserved_on}"
        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        self.qr_code.save(f"{self.id}_qr.png", ContentFile(buffer.read()), save=False)
        buffer.close()
