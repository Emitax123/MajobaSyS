"""
Filtros para proyectos en la API REST de MajobaSyS.
"""
import django_filters

from manager.models import Project


class ProjectFilter(django_filters.FilterSet):
    """
    Filtro para el listado de proyectos.
    Permite filtrar por cliente, estado activo y rango de fechas.
    """
    client = django_filters.NumberFilter(
        field_name='client_id',
        help_text='Filtrar por ID de cliente',
    )
    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        help_text='Filtrar por estado activo/inactivo',
    )
    start_date_from = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        help_text='Fecha de inicio desde (YYYY-MM-DD)',
    )
    start_date_to = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        help_text='Fecha de inicio hasta (YYYY-MM-DD)',
    )

    class Meta:
        model = Project
        fields = ['client', 'is_active', 'start_date_from', 'start_date_to']
