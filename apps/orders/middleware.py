from orders.models import Order


class OrderMiddleware(object):

    def process_request(self, request):
        "Auto create session order if it doesn't already exist"
        if 'order_id' not in request.session:
            order = Order.objects.create()
            request.session['order_id'] = order.pk
