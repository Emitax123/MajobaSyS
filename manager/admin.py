from django.contrib import admin
from .models import ManagerData, Project, Notification

# Register your models here.
admin.site.register(ManagerData)
admin.site.register(Project)
admin.site.register(Notification)
