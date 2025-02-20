from django.db import models
import django.core.validators
from django.conf import settings


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0
    )  # Calculé automatiquement à partir des notes

    def __str__(self):
        return self.name

    def update_rating(self):
        """Met à jour la note moyenne de l'hôtel."""
        ratings = self.ratings.all()
        self.average_rating = (
            sum(rating.rating for rating in ratings) / len(ratings)
            if ratings.exists()
            else 0.0
        )
        self.save()

    def get_first_image(self):
        """Retourne la première image de l'hôtel ou None si aucune image n'est disponible."""
        first_image = self.images.first()  # Utilisation de `related_name`
        return first_image.image.url if first_image else None


class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="hotel_images/")
    is_featured = models.BooleanField(default=False)  # Image mise en avant

    def __str__(self):
        return f"Image for {self.hotel.name}"


class RoomType(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Standard", "Deluxe", "Suite"
    description = models.TextField(null=True, blank=True)
    max_people = models.PositiveIntegerField()  # Maximum number of people

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type.name} - {self.room_number}"


class RoomRate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="rates")
    start_date = models.DateField()
    end_date = models.DateField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.room} - {self.start_date} to {self.end_date}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("Confirmed", "Confirmed"),
        ("Pending", "Pending"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reservations")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="reservations")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_people = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"Reservation {self.id} - {self.user.username} - {self.hotel.name}"


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveIntegerField(
        validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]
    )  # Notes entre 1 et 5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} - {self.rating} stars"

    class Meta:
        unique_together = ("user", "hotel")  # Un utilisateur ne peut noter un hôtel qu'une fois
