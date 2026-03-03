from django import forms

from .models import Client, ManagerData, Project


class ManagerDataForm(forms.ModelForm):
    class Meta:
        model = ManagerData
        fields = '__all__'
        exclude = ['user']


class ClientForm(forms.ModelForm):
    """
    Formulario para crear o modificar un cliente.
    """
    class Meta:
        model = Client
        fields = ['name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Nombre del cliente'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Teléfono del cliente'})


class ProjectForm(forms.ModelForm):
    """
    Formulario para crear o modificar un proyecto.
    Acepta el kwarg ``user`` para filtrar el selector de clientes
    mostrando solo los clientes que pertenecen al usuario autenticado.
    """
    start_date = forms.DateField(
        input_formats=['%d-%m-%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        input_formats=['%d-%m-%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    client = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        required=True,
        empty_label='— Seleccionar cliente —',
        label='Cliente',
    )

    class Meta:
        model = Project
        fields = ['client', 'name', 'description', 'location', 'start_date', 'end_date', 'is_active']

    def __init__(self, *args, **kwargs):
        # Extraer el kwarg ``user`` antes de llamar a super()
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filtrar el queryset de clientes al usuario indicado
        if user is not None:
            self.fields['client'].queryset = Client.objects.filter(user=user)

        # Inicializar fechas para que el widget de tipo date las muestre correctamente
        if self.instance and self.instance.pk:
            if self.instance.start_date:
                self.initial['start_date'] = self.instance.start_date.strftime('%Y-%m-%d')
            if self.instance.end_date:
                self.initial['end_date'] = self.instance.end_date.strftime('%Y-%m-%d')

        # Placeholders y etiquetas
        self.fields['name'].widget.attrs.update({'placeholder': 'Nombre del proyecto'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Descripción del proyecto'})
        self.fields['location'].widget.attrs.update({'placeholder': 'Ubicación del proyecto'})
        self.fields['start_date'].widget.attrs.update({'placeholder': 'Fecha de inicio'})
        self.fields['end_date'].widget.attrs.update({'placeholder': 'Fecha de fin (opcional)'})
        self.fields['is_active'].label = '¿Está activo?'
