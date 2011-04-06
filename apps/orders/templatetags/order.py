from django import template
from django.http import QueryDict
from django.core.urlresolvers import reverse

from orders.utils import content_type


register = template.Library()


class OrderNode(template.Node):
    def __init__(self, *args):
        self.obj_var = template.Variable(args[0])

    def render(self, context):
        self.obj = self.obj_var.resolve(context)
        self.ct = content_type(self.obj)
        self.params = QueryDict(None).copy()


class AddItemNode(OrderNode):
    def __init__(self, obj, qty):
        super(AddItemNode, self).__init__(obj)
        self.qty = qty

    def render(self, context):
        super(AddItemNode, self).render(context)
        self.params.update(
            {'ct': self.ct.pk, 'pk': self.obj.pk, 'q': self.qty})
        return '%s?%s' % (reverse('add_to_order'), self.params.urlencode())


class RemoveItemNode(OrderNode):
    def render(self, context):
        super(RemoveItemNode, self).render(context)
        self.params.update({'ct': self.ct.pk, 'pk': self.obj.pk})
        return '%s?%s' % (reverse('remove_from_order'), self.params.urlencode())


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
