import logging

from django.core.urlresolvers import reverse
from django.views.generic import edit
from django.forms.models import modelform_factory, inlineformset_factory
from django.contrib import messages
from django.utils.translation import ugettext as _

from orders.models import Order, Item
from orders.forms import ItemForm


class OrderMixin(object):
    model = Item

    def get_success_url(self):
        return reverse('order:review')


class OrderView(OrderMixin, edit.UpdateView):
    "Change quantity of or delete multiple items in order"

    model = Order
    form_class = inlineformset_factory(Order, Item, form=ItemForm, extra=0)

    def get_object(self, *args, **kwargs):
        return get_order(self.request)

    def get_form_kwargs(self):
        kwargs = {'instance': self.get_object()}
        if self.request.method == 'POST':
            kwargs = dict(data=self.request.POST, **kwargs)
        return kwargs

    def form_valid(self, form):
        messages.info(self.request, _('Your order has been updated'))
        return super(OrderView, self).form_valid(form)


class AddItemView(OrderMixin, edit.CreateView):

    def get_form_class(self):
        return modelform_factory(self.model, exclude=['order'])

    def form_invalid(self, form):
        messages.error(self.request, _('Invalid Item'))
        return super(AddItemView, self).form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        product, qty = self.object.product, self.object.quantity
        get_order(self.request).add(product, qty)
        messages.success(self.request,
            _('%i x %s added to your basket' % (qty, product)))
        return edit.FormMixin.form_valid(self, form)

    def get(self, request, *args, **kwargs):
        raise NotImplementedError('Get is not possible here')


class RemoveItemView(OrderMixin, edit.DeleteView):

    def get_object(self, *args, **kwargs):
        obj = self.model.objects.get(
            order=get_order(self.request),
            content_type=self.kwargs['content_type'],
            object_id=self.kwargs['object_id'])
        messages.info(self.request, _('%s removed' % obj))
        return obj

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


def get_order(request):
    "Helper to get a user's order from session"
    order_id = request.session.get('order_id', None)
    order, created = Order.objects.get_or_create(pk=order_id)
    if created:
        request.session['order_id'] = order.pk
    return order
