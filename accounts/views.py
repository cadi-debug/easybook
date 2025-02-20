from cinetpay_sdk.s_d_k import Cinetpay
from django.contrib import messages
from django.contrib.auth import login, get_user_model, authenticate, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from hotel.models import Reservation
from hotel.utils import generate_transaction_id, calculate_total_price



User = get_user_model()


def index(request):
    return render(request, 'accounts/home.html')


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Vérification côté serveur (pour éviter les failles JS)
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return redirect("accounts:signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect("accounts:signup")

        if len(password) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères.")
            return redirect("accounts:signup")

        # Création du compte
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        messages.success(request, "Inscription réussie !")
        return redirect("accounts:home")

    return render(request, "accounts/signup.html")


# AJAX view for checking username and password availability
def check_availability(request):
    username = request.GET.get("username", None)
    email = request.GET.get("email", None)
    response = {}

    if username:
        response["username_exists"] = User.objects.filter(username=username).exists()

    if email:
        response["email_exists"] = User.objects.filter(email=email).exists()

    return JsonResponse(response)


def login_user(request):
    if request.method == "POST":
        # Getting date from login form
        username = request.POST.get("username")
        password = request.POST.get("password")

        # User authentication
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Connexion réussie
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    # Display form
    return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'accounts/reservation_hotels.html', {'reservations': reservations})

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if reservation.status != 'Cancelled':
        reservation.status = 'Cancelled'
        reservation.save()
    return redirect('accounts:my_reservations')

@login_required
def pay_reservation(request, reservation_id):
    # Payment handling logic will be implemented later
    return redirect('accounts:my_reservations')


@login_required(login_url='accounts:login')
def get_paid(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == 'POST':
        client = Cinetpay("2974129567ae8683ebe596.51238957", "105887849")
        data = {
            'amount': reservation.total_price,
            'currency': "CDF",
            'transaction_id': generate_transaction_id(),
            'description': f"Payment for reservation {reservation.id} at {reservation.hotel.name}",
            'return_url': "http://127.0.0.1:8000/hotel/success/",
            'notify_url': "http://127.0.0.1:8000/hotel/notify/",
            'customer_name': request.user.first_name,
            'customer_surname': request.user.last_name,
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
