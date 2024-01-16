from django import forms

class PValueForm(forms.Form):
    inlineRadioOptions = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        choices=(
            ('0.01', '0.01'),
            ('0.05', '0.05'),
            ('0.10', '0.10'),
        ),
        initial='0.01'  # Set the initial selection if needed
    )