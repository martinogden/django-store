from django.contrib.contenttypes.models import ContentType

# Shortcut to get an items content type
content_type = lambda product: ContentType.objects.get_for_model(product)