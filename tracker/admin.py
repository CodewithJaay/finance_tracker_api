from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Account, Category, Transaction, Budget, Goal

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'account_type', 'balance', 'created_at')
    search_fields = ('name', 'user__email', 'user__username')
    list_filter = ('created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "user")
    list_filter = ("category_type",)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_type", "amount", "account", "category", "date")
    list_filter = ("transaction_type", "date", "category")
    search_fields = ("description",)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "month", "amount")

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "target_amount", "current_amount", "deadline")
    search_fields = ("name",)