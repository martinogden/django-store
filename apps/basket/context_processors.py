from basket.models import Basket

def basket(request):
    basket_id = request.session.get('basket_id')
    return {
        'basket': Basket.objects.get(pk=basket_id)
    }
