import logging
logger = logging.getLogger('django')
from django import template, forms, http
from django.core.urlresolvers import reverse

from orders.utils import content_type
from orders.models import Item

register = template.Library()


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if key != 'quantity':
                field.widget = forms.widgets.HiddenInput()
    class Meta:
        model = Item


class OrderNode(template.Node):
    def __init__(self, *args):
        self.obj_var = template.Variable(args[0])

    def render(self, context):
        obj = self.obj_var.resolve(context)
        self.item = Item(object_id=obj.pk,\
            content_type_id=content_type(obj))


class AddItemNode(OrderNode):
    def __init__(self, obj, qty):
        super(AddItemNode, self).__init__(obj)
        self.qty = qty

    def render(self, context):
        super(AddItemNode, self).render(context)
        self.item.quantity = self.qty
        self.form = ItemForm(instance=self.item)
        # self.form.save(commit=False)
        # self.form.quantity = self.qty
        context['form'] = self.form
        logger.info(self.form)
        return template.Template("""<form action={% url order:add-item %} method="post">
    {% csrf_token %}
    {{ form }}
    <input type="submit" value="Add to Order">
</form>""").render(template.Context(context))


class RemoveItemNode(OrderNode):
    def render(self, context):
        super(RemoveItemNode, self).render(context)
        query_dict = http.QueryDict(None).copy()
        query_dict.update({'ct': self.item.content_type_id, 'pk': self.item.object_id})
        return '%s?%s' % (reverse('order:remove-item'), query_dict.urlencode())


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

@register.tag
def remove_from_order(parser, token):
    """
    Return a url to remove an item from the users order
    
    Usage:
        
        {% remove_from_order object %}
    """
    bits = token.contents.split()
    
    if not len(bits) == 2:
        raise template.TemplateSyntaxError('%s takes exactly 1 arguments' % bits[0])

    obj = bits[1]
    return RemoveItemNode(obj)
