# import logging
# logger = logging.getLogger('django')

from django import template, forms, http
from django.core.urlresolvers import reverse

from orders.utils import content_type
from orders.models import Item
from orders.forms import ItemForm


register = template.Library()


class AddItemNode(template.Node):
    def __init__(self, obj, qty):
        self.obj_var, self.qty = template.Variable(obj), qty

    def render(self, context):
        obj = self.obj_var.resolve(context)
        self.item = Item(object_id=obj.pk, content_type_id=content_type(obj))
        self.item.quantity = self.qty
        self.form = ItemForm(instance=self.item)
        context['form'] = self.form
        return template.Template("""<form action={% url order:add-item %} method="post">
    {% csrf_token %}
    {{ form }}
    <input type="submit" value="Add to Order">
</form>""").render(template.Context(context))


@register.tag
def add_to_order(parser, token):
    """
    Return a url to add x items to the users order
    
    Usage:
        
        {% add_to_order object %}
        - OR -
        {% add_to_order object 10 %}
    """
    bits = token.contents.split()
    
    if len(bits) == 2:
        qty = 1
    elif len(bits) == 3:
        qty = int(bits[2])
    else:
        raise template.TemplateSyntaxError('%s takes either 1 or 2 arguments' % bits[0])

    obj = bits[1]
    return AddItemNode(obj, qty)
