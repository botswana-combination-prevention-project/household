from django import forms


class GpsSearchForm(forms.Form):

    degrees_s = forms.IntegerField(label='S', required=True)
    minutes_s = forms.DecimalField(label='.', required=True)
    degrees_e = forms.IntegerField(label='E', required=True)
    minutes_e = forms.DecimalField(label='.', required=True)
    radius = forms.DecimalField(label='R (m)', required=True)

    def clean_degree_s(self):
        degrees_s = self.cleaned_data['degrees_s']
        if degrees_s is None:
            raise forms.ValidationError("S is required")
        return degrees_s
