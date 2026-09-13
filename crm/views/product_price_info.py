from decimal import Decimal
from django.apps import apps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def product_price_info(request):
    """Calculate amount for given product, quantity, tier_name and deal currency.

    Expects GET params via query string:
    - product: product id
    - quantity: numeric quantity
    - tier_name: id of ClientType (price tier)
    - deal_currency: id of Currency used in deal

    Returns JSON: {'ok': True, 'amount': '123.45'} or {'ok': False, 'error': '...'}
    """
    Product = apps.get_model('crm', 'Product')
    ProductPriceTier = apps.get_model('crm', 'ProductPriceTier')
    Currency = apps.get_model('crm', 'Currency')

    product_id = request.GET.get('product')
    quantity = request.GET.get('quantity')
    tier_name = request.GET.get('tier_name')
    deal_currency_id = request.GET.get('deal_currency')

    # validate inputs
    if not product_id or not tier_name or not deal_currency_id:
        return JsonResponse({'ok': False, 'error': 'missing_params'})

    try:
        product = Product.objects.get(pk=int(product_id))
    except Exception:
        return JsonResponse({'ok': False, 'error': 'product_not_found'})

    try:
        qty = Decimal(quantity) if quantity is not None and quantity != '' else Decimal(0)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'bad_quantity'})

    # Determine currency of the price tier: prefer product.currency, else department.default_currency
    product_currency = None
    if getattr(product, 'currency_id', None):
        product_currency = Currency.objects.filter(pk=product.currency_id).first()
    else:
        try:
            Department = apps.get_model('common', 'Department')
            dept = Department.objects.filter(pk=product.department_id).first()
            if dept and getattr(dept, 'default_currency_id', None):
                product_currency = Currency.objects.filter(pk=dept.default_currency_id).first()
        except Exception:
            product_currency = None

    # find price tier for product and tier_name
    price_tier = None
    try:
        price_tier = ProductPriceTier.objects.filter(
            product=product, tier_name_id=int(tier_name)
        ).order_by('-min_quantity').first()
    except Exception:
        price_tier = None

    if not price_tier:
        return JsonResponse({'ok': False, 'error': 'no_price_tier'})

    price = price_tier.price

    # find deal currency rates
    deal_currency = Currency.objects.filter(pk=int(deal_currency_id)).first()
    if not deal_currency:
        return JsonResponse({'ok': False, 'error': 'deal_currency_not_found'})

    # if product_currency is missing, assume price already in deal currency
    if not product_currency:
        amount = (price * qty).quantize(Decimal('0.01'))
        return JsonResponse({'ok': True, 'amount': str(amount)})

    # convert price from product_currency -> state -> deal_currency
    # price_in_state = price * product_currency.rate_to_state_currency
    # price_in_deal = price_in_state / deal_currency.rate_to_state_currency
    try:
        rate_prod = Decimal(product_currency.rate_to_state_currency)
        rate_deal = Decimal(deal_currency.rate_to_state_currency)
        if rate_deal == 0:
            return JsonResponse({'ok': False, 'error': 'zero_deal_rate'})
        price_in_deal = (price * rate_prod / rate_deal)
        amount = (price_in_deal * qty).quantize(Decimal('0.01'))
        return JsonResponse({'ok': True, 'amount': str(amount)})
    except Exception:
        return JsonResponse({'ok': False, 'error': 'calc_error'})
