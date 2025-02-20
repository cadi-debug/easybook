from django.db import models
from django.conf import settings
from decimal import Decimal


class Category(models.Model):
    title = models.CharField(max_length=200)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)

    def __str__(self):
        return self.title


class Mark(models.Model):
    title = models.CharField(max_length=200)
    rating = models.DecimalField(max_digits=10, decimal_places=2 ,default=1.0)
    year = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.year})"


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    mark = models.ForeignKey(Mark, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (f"Reservation by {self.user.username} for {self.mark.title} in {self.category.title} from "
                f"{self.start_date} to {self.end_date}")

    def calculate_price(self):
        base_price = 50.0
        age_index = 1 + (2025 - self.mark.year.year) // 10
        price = Decimal(base_price) * (Decimal(self.category.rating) + Decimal(self.mark.rating)) * Decimal(age_index)
        return round(price, 2)