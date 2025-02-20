from django.shortcuts import render, redirect
from .models import Category, Mark, Reservation
from .forms import ReservationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date


@login_required
def reserve_car(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user

            # Conversion explicite des dates (si nécessaire)
            """if isinstance(reservation.start_date, str):
                reservation.start_date = date.fromisoformat(reservation.start_date)
            if isinstance(reservation.end_date, str):
                reservation.end_date = date.fromisoformat(reservation.end_date)"""

            # Vérification des conflits de réservation
            existing_reservations = Reservation.objects.filter(
                category=reservation.category,
                mark=reservation.mark,
                start_date__lt=reservation.end_date,
                end_date__gt=reservation.start_date
            )

            if not existing_reservations.exists():
                reservation.save()
                messages.success(request, 'Your reservation has been confirmed.')
                return redirect('cars:confirmation')
            else:
                messages.error(request, 'The car is already reserved for the selected dates.')
    else:
        form = ReservationForm()

    # Gestion des cas GET et des erreurs de validation
    categories = Category.objects.all()
    marks = Mark.objects.all()
    return render(request, 'cars/reservations.html', {
        'form': form,
        'categories': categories,
        'marks': marks,
    })


def confirmation(request):
    last_reservation = Reservation.objects.filter(user=request.user).last()
    price = last_reservation.calculate_price() if last_reservation else 0
    return render(request, 'cars/confirmation.html', {'price':price})