from django import forms

from .models import ManagerData

class ManagerDataForm(forms.ModelForm):
    class Meta:
        model = ManagerData
        fields = '__all__'
        exclude = ['user']
        