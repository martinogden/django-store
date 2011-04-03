from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.http import Http404

from catalog.models import Product


class ProductDetailView(DetailView):
    def get_object(self, *args):
        """
        Overridden to allow us to get an object using pk AND slug
            Code mostly lifted from django.views.generic.detail.DetailView#get_object
        """

        pk = self.kwargs.get('pk', None)
        slug = self.kwargs.get('slug', None)
        slug_field = self.get_slug_field()
        kwargs = {slug_field: slug, 'pk': pk}

        if pk is not None and slug is not None:
            queryset = self.get_queryset().filter(**kwargs)
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"both an object pk and a slug."
                                 % self.__class__.__name__)
        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj
