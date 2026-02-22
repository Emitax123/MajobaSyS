from django import forms

from .models import ManagerData, Project

class ManagerDataForm(forms.ModelForm):
    class Meta:
        model = ManagerData
        fields = '__all__'
        exclude = ['user']
        
class ProjectForm(forms.ModelForm):
    start_date = forms.DateField(
        input_formats=['%d-%m-%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        input_formats=['%d-%m-%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'location', 'start_date', 'end_date', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%d')
            if self.instance.end_date:
                self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%d')
        self.fields['name'].widget.attrs.update({'placeholder': 'Nombre del proyecto'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Descripción del proyecto'})
        self.fields['location'].widget.attrs.update({'placeholder': 'Ubicación del proyecto'})
        self.fields['start_date'].widget.attrs.update({'placeholder': 'Fecha de inicio'})
        self.fields['end_date'].widget.attrs.update({'placeholder': 'Fecha de fin (opcional)'})
        self.fields['is_active'].label = '¿Está activo?'


