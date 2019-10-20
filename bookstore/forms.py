from django import forms

PAYMENT_CHOICES = (
    ('P', 'Paypal'),
    ('S', 'Stripe')
)
class CheckoutForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    address = forms.CharField()
    country = forms.CharField()
    city = forms.CharField()
    zip = forms.CharField()
    save_info = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    use_default_info = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

class PromocodeForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'validate',
        'id': 'promocode',
        'placeholder': 'Your promo here..',
        'label': 'Promocode',
    }))

class RefundForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea)