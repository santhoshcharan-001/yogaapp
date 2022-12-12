from django.contrib import admin
from django.contrib.auth.models import Group
from .models import UserProfile, Batch, Payment

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Batch)
admin.site.register(Payment)
admin.site.unregister(Group)
