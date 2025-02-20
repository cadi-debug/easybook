def calculate_total_price(reservation):
    days = (reservation.check_out_date - reservation.check_in_date).days
    price_per_day = reservation.room.price_per_day
    return days * price_per_day * reservation.number_of_people


def generate_transaction_id():
    import uuid
    return str(uuid.uuid4())