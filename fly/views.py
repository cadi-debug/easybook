import qrcode
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from reportlab.pdfgen import canvas
from fly.models import Flight, Reservation
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from cinetpay_sdk.s_d_k import Cinetpay

def search_flights(request):
    """Search available flights"""
    flights = Flight.objects.all()
    departure = arrival = flight_class = ""

    if request.method == 'GET':
        departure = request.GET.get('departure', "").strip()
        arrival = request.GET.get('arrival', "").strip()
        flight_class = request.GET.get('flight_class', "").strip()

        if departure:
            flights = flights.filter(departure_airport__name__icontains=departure)
        if arrival:
            flights = flights.filter(arrival_airport__name__icontains=arrival)
        if flight_class:
            flights = flights.filter(flight_class=flight_class)

    return render(request, 'fly/search_flight.html', {
        'flights': flights,
        'departure': departure,
        'arrival': arrival,
        'flight_class': flight_class,
    })


@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    total_reservations = Reservation.objects.filter(flight=flight).aggregate(total=models.Sum('passengers'))['total'] or 0
    available_seats = 100 - total_reservations

    if request.method == 'POST':
        passengers = int(request.POST.get('passengers'))

        if passengers > available_seats:
            return render(request, 'fly/book_flight.html', {
                'flight': flight,
                'error': f"Seulement {available_seats} sièges disponibles.",
            })

        # Créer la réservation
        reservation = Reservation.objects.create(user=request.user, flight=flight, passengers=passengers)

        # Générer le QR code
        qr_data = f"Réservation ID: {reservation.id}, Vol: {flight.flight_number}, Utilisateur: {request.user.username}"
        qr_image = qrcode.make(qr_data)

        # Sauvegarder le QR code dans le champ qr_code
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_file = ContentFile(buffer.getvalue(), f"qr_{reservation.id}.png")
        reservation.qr_code.save(f"qr_{reservation.id}.png", qr_file)

        return render(request, 'fly/booking_confirmation.html', {
            'flight': flight,
            'passengers': passengers,
            'reservation': reservation,
        })

    return render(request, 'fly/book_flight.html', {
        'flight': flight,
        'available_seats': available_seats,
    })


@login_required
def download_ticket(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Configuration de la réponse HTTP pour le fichier PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{reservation.id}.pdf"'

    # Préparer le buffer pour générer le PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading2"]
    body_style = styles["BodyText"]
    centered_style = styles["BodyText"]
    centered_style.alignment = 1  # Centrer le texte

    # Contenu du PDF
    elements = []

    # Titre principal
    elements.append(Paragraph("Votre billet est prêt !", title_style))
    elements.append(Spacer(1, 20))

    # Bloc avec les détails du vol et de la réservation
    elements.append(Paragraph("Détails du vol", subtitle_style))
    flight_details = [
        ["Numéro du vol :", reservation.flight.flight_number],
        ["Compagnie aérienne :", reservation.flight.airline],
        ["Ville de départ :", reservation.flight.departure_city],
        ["Ville d'arrivée :", reservation.flight.arrival_city],
        ["Heure de départ :", reservation.flight.departure_time.strftime("%Y-%m-%d %H:%M")],
        ["Heure d'arrivée :", reservation.flight.arrival_time.strftime("%Y-%m-%d %H:%M")],
    ]

    reservation_details = [
        ["Réservation ID :", str(reservation.id)],
        ["Nombre de passagers :", str(reservation.passengers)],
        ["Utilisateur :", reservation.user.username],
    ]

    # Créer les tables pour une mise en page structurée
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])

    flight_table = Table(flight_details, colWidths=[150, 300])
    flight_table.setStyle(table_style)
    elements.append(flight_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Détails de la réservation", subtitle_style))
    reservation_table = Table(reservation_details, colWidths=[150, 300])
    reservation_table.setStyle(table_style)
    elements.append(reservation_table)
    elements.append(Spacer(1, 20))

    # QR Code
    elements.append(Paragraph("Votre QR Code", subtitle_style))
    if reservation.qr_code:
        qr_code_path = reservation.qr_code.path
        try:
            qr_image = Image(qr_code_path, width=200, height=200)
            elements.append(qr_image)
        except Exception:
            elements.append(Paragraph("Erreur lors du chargement du QR Code.", body_style))
    else:
        elements.append(Paragraph("Aucun QR Code disponible.", body_style))

    # Générer le PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)
    return response


