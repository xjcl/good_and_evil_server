from django import forms

class GaeParamsForm(forms.Form):
    hex_color = forms.CharField(label='hex_color', max_length=7,
        widget=forms.TextInput(attrs={'type': 'color', 'onInput': 'form_input();'}))
    str1 = forms.CharField(label='str1', max_length=40, initial='TALLY',
        widget=forms.TextInput(attrs={'onInput': 'form_input();'}))
    str2 = forms.CharField(label='str2', max_length=40, initial='HALL',
        widget=forms.TextInput(attrs={'onInput': 'form_input();'}))
    font_size = forms.IntegerField(label='font_size', min_value=1, max_value=400,
        widget=forms.NumberInput(attrs={'value': 70, 'onInput': 'form_input();'}))
