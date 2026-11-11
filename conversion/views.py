from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.http import JsonResponse
from django.views.decorators.http import require_GET


RATES_TO_GBP = {
    'GBP': Decimal('1.0'),
    'USD': Decimal('0.77'),
    'EUR': Decimal('0.86'),
}

SUPPORTED_CURRENCIES = set(RATES_TO_GBP.keys())


def quantize_money(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_conversion(currency1, currency2, amount):
    currency1 = currency1.upper()
    currency2 = currency2.upper()

    if currency1 not in SUPPORTED_CURRENCIES or currency2 not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported currency.")

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid amount.")

    rate = RATES_TO_GBP[currency1] / RATES_TO_GBP[currency2]
    converted = amount * rate

    return rate.quantize(Decimal('0.0001')), quantize_money(converted)


@require_GET
def conversion(request, currency1, currency2, amount):
    try:
        rate, converted_amount = calculate_conversion(currency1, currency2, amount)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    return JsonResponse({
        'from_currency': currency1.upper(),
        'to_currency': currency2.upper(),
        'original_amount': str(amount),
        'conversion_rate': str(rate),
        'converted_amount': str(converted_amount),
    })
