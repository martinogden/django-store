from django.contrib.contenttypes.models import ContentType

# Shortcut to get an items content type
content_type = lambda product: ContentType.objects.get_for_model(product)


def get_object(ct_pk, pk):
    "Return an instance of the item defined by it's content type and the instance pk"
    try:
        model = ContentType.objects.get(pk=ct_pk)
        item = model.get_object_for_this_type(pk=pk)
    except ObjectDoesNotExist:
        return None
    else:
        return item
