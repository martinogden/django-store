from django.dispatch import Signal

checkout_started = Signal(providing_args=['request'])
