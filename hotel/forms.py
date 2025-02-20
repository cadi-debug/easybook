from django import forms
from django.core.exceptions import ValidationError

from .models import Reservation, Rating


# Reservation form
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['check_in_date', 'check_out_date', 'number_of_people', 'room']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')

        if check_in_date and check_out_date and check_in_date >= check_out_date:
            raise ValidationError("La date d'arrivée doit être antérieure à la date de départ.")

        return cleaned_data


# Rating form
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating", "comment"]
