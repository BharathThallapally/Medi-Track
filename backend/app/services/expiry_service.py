from datetime import date


def get_expiry_status(expiry_date: date):
    today = date.today()

    days_remaining = (expiry_date - today).days

    if days_remaining < 0:
        status = "EXPIRED"

    elif days_remaining <= 9:
        status = "EXPIRING_SOON"

    elif days_remaining <= 15:
        status = "EXPIRY_WARNING"

    else:
        status = "NORMAL"

    return {
        "days_remaining": days_remaining,
        "status": status
    }