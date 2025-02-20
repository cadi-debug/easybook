from datetime import datetime
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from .models import Hotel
from .forms import ReservationForm, RatingForm
from django.views import generic
from django.contrib import messages
from django.shortcuts import redirect
from cinetpay_sdk.s_d_k import Cinetpay
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import uuid


def generate_transaction_id(prefix='TXN'):

    unique_id = uuid.uuid4().hex[:8]
    date_str = datetime.now().strftime('%Y%m%d%H%M%S')

    transaction_id = f"{prefix}-{date_str}-{unique_id}"
    return transaction_id

class HotelView(generic.ListView):
    template_name = 'hotel/hotels.html'
    context_object_name = "exclusive_hotels"
    hotels = Hotel.objects.all()[:10]
    best_hotels = Hotel.objects.order_by('-average_rating')[:6]
    top_hotels = Hotel.objects.annotate(reservation_count=Count('reservations')).order_by('-reservation_count')[:6]

    def get_queryset(self):
        if self.best_hotels:
            return self.best_hotels
        elif self.top_hotels:
            return self.top_hotels
        else:
            return self.hotels


class HotelDetail(LoginRequiredMixin, generic.DetailView):
    model = Hotel
    template_name = 'hotel/hotel_reservation.html'
    login_url = 'accounts:login'  # Redirection si l'utilisateur n'est pas connecté

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation_form'] = ReservationForm()
        context['rating_form'] = RatingForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Récupérer l'objet Hotel
        hotel = self.object

        reservation_form = ReservationForm()
        rating_form = RatingForm()

        if "reserve" in request.POST:
            reservation_form = ReservationForm(request.POST)
            if reservation_form.is_valid():
                reservation = reservation_form.save(commit=False)
                reservation.user = request.user
                reservation.hotel = hotel
                reservation.total_price = calculate_total_price(reservation)
                reservation.save()
                messages.success(request, "Votre réservation a été effectuée avec succès.")
                return redirect("hotel:detail", pk=hotel.id)

        elif "rate" in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.user = request.user
                rating.hotel = hotel
                rating.save()
                messages.success(request, "Merci pour votre évaluation.")
                return redirect("hotel_detail", pk=hotel.id)

        # Si les formulaires sont invalides, on les renvoie dans le contexte
        context = self.get_context_data(object=self.object)
        context['reservation_form'] = reservation_form
        context['rating_form'] = rating_form
        return self.render_to_response(context)

def calculate_total_price(reservation):
    days = (reservation.check_out_date - reservation.check_in_date).days
    price_per_day = reservation.room.price_per_day
    return days * price_per_day * reservation.number_of_people


def search_hotels(request):
    query = request.GET.get('q', '')
    hotels = Hotel.objects.filter(name__icontains=query).values('id', 'name')
    return JsonResponse(list(hotels), safe=False)

"""
@login_required(login_url='accounts:login')
def get_paid(request):
    if request.method == 'POST':
        client = Cinetpay("2974129567ae8683ebe596.51238957", "105887849")
        data = {
            'amount': 1000,
            'currency': "CDF",
            'transaction_id': generate_transaction_id(),
            'description': "TRANSACTION DESCRIPTION",
            'return_url': "http://127.0.0.1:8000/hotel/success/",
            'notify_url': "http://127.0.0.1:8000/hotel/notify/",
            'customer_name': "cadi",
            'customer_surname': "KAMBAJI",
        }
        # Init payment
        direct = client.PaymentInitialization(data)
        if direct.get('code') == '201':
            payment_url = direct.get('data', {}).get('payment_url')
            if payment_url:
                return HttpResponseRedirect(payment_url)
            else:
                return JsonResponse({'error': 'URL de paiement manquante'})
        else:
            error_message = direct.get('message', 'Erreur inconnue')
            return JsonResponse({"error": error_message})
    else:
        return HttpResponseRedirect(reverse('accounts:login'))

"""