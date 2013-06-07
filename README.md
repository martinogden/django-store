# Django Store
---

### Goals

 * A simple / flexible django-based store.

 * Any model with a price attribute can be added to the order (basket) via django's built in [generic relations](https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/).

 * Payment and Shipping modules can be plugged in, and choices offered to the user on checkout.

 * Checkout should be simple (a single page if possible) and be able to easily integrate with many payment providers

 * Possibility to include a download with an item, which can be downloaded an arbitrary amount of times or within a set time period.


### User Journey

* When user first interacts with the basket, an Order is created and associated with the users session - this session should persist as long as possible

* The basket has many items. All baskets are persisted on the database

* Any model instance with a price attribute can be added to the basket, using the content types / generic relationships built into Django

* Items are added to the basket via a POST request - Form created by a templatetag

* the order is marked as pending and the basket marked as immutable until a completed or cancelled response is received from the payment gateway

* a payment response is received and a signal sent out. order is marked as complete or cancelled

* when order changes status a signal should be sent out, if the status is completed, delivery should be initiated (download link activated, email sent, kunaki order sent)

  N.B there should be an order status lower than pending (suggest 'created') where the basket is still mutable. It should be escalated to a 'pending' status when a call has been sent off to the payment gateway

* download link should be a redirect to a masked link on amazon S3, allowing 3 download attempts


 ---
### Licence

<a rel="license" href="http://creativecommons.org/licenses/by/3.0/"><img alt="Creative Commons License" style="border-width:0" src="http://i.creativecommons.org/l/by/3.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">Creative Commons Attribution 3.0 Unported License</a>.