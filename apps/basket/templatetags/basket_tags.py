from django import template
from django.http import QueryDict
from django.core.urlresolvers import reverse

from basket.utils import content_type


register = template.Library()


class BasketNode(template.Node):
    def __init__(self, *args):
        self.obj_var = template.Variable(args[0])

    def render(self, context):
        self.obj = self.obj_var.resolve(context)
        self.ct = content_type(self.obj)
        self.params = QueryDict(None).copy()


class AddItemNode(BasketNode):
    def __init__(self, obj, qty):
        super(AddItemNode, self).__init__(obj)
        self.qty = qty

    def render(self, context):
        super(AddItemNode, self).render(context)
        self.params.update(
            {'ct': self.ct.pk, 'pk': self.obj.pk, 'q': self.qty})
        return '%s?%s' % (reverse('add_to_basket'), self.params.urlencode())


class RemoveItemNode(BasketNode):
    def render(self, context):
        super(RemoveItemNode, self).render(context)
        self.params.update({'ct': self.ct.pk, 'pk': self.obj.pk})
        return '%s?%s' % (reverse('remove_from_basket'), self.params.urlencode())


@register.tag
def add_to_basket(parser, token):
    """
    Return a url to add x items to the basket
    
    Usage:
        
        {% add_to_basket object %}
        - OR -
        {% add_to_basket object 10 %}
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
def remove_from_basket(parser, token):
    """
    Return a url to remove an item from the basket
    
    Usage:
        
        {% remove_from_basket object %}
    """
    bits = token.contents.split()
    
    if not len(bits) == 2:
        raise template.TemplateSyntaxError('%s takes exactly 1 arguments' % bits[0])

    obj = bits[1]
    return RemoveItemNode(obj)
