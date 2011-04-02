from basket.models import Basket


class BasketMiddleware(object):

    def process_request(self, request):
        request.session['basket'] = Basket.objects.create()
