from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'balance', 'created_at')
    search_fields = ('name', 'user_email')
    list_filter = ('created_at',)