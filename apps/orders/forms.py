from django import forms

from orders.models import Item


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if key != 'quantity':
                field.widget = forms.widgets.HiddenInput()

    class Meta:
        model = Item
