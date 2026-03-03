from django.contrib import admin
from .models import Client, ManagerData, Project, Notification

# Register your models here.
admin.site.register(Client)
admin.site.register(ManagerData)
admin.site.register(Project)
admin.site.register(Notification)
