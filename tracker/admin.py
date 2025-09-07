from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.http import HttpResponse 
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum
import csv
from .models import Account, Category, Transaction, Budget, Goal
from django.shortcuts import redirect
from django.db.models.functions import TruncMonth


#Inline for Transactions in Account
class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 1
    fields = ('transaction_type', 'amount', 'currency', 'category', 'date')
    readonly_fields = ('date', 'created_at',)
    
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'currency', 'account_type', 'balance', 'created_at')
    search_fields = ('name', 'user__email', 'user__username')
    list_filter = ('account_type','currency','created_at',)
    ordering = ('-created_at',)
    inlines = [TransactionInline] #Show Transaction inside Account

#Inline for Transaction in Category
class TransactionCategoryInline(admin.TabularInline):
    model = Transaction
    extra = 1
    fields = ('transaction_type', 'amount', 'currency', 'category', 'date')
    readonly_fields = ('date',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'user', 'created_at')
    list_filter = ('category_type',)
    search_fields = ('name', 'user__email', 'user__username')
    ordering = ('name', 'category_type')
    inlines = [TransactionCategoryInline] #Show Transaction inside Category

# Transaction Admin with CSV Export

def export_transactions_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=transactions.csv'
    writer = csv.writer(response)
    writer.writerow(['User', 'Account', 'Category', 'Type', 'Amount', 'Currency', 'Date'])

    for t in queryset:
        writer.writerow([
            t.user.email if hasattr(t.user, 'email') else t.user.username,
            t.account.name,
            t.category.name,
            t.transaction_type,
            t.amount,
            t.currency,
            t.date,
        ])

    return response

export_transactions_to_csv.short_description = "Export selected transactions to CSV"

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'amount', 'account', 'category', 'date')
    list_filter = ('transaction_type', 'date', 'category')
    search_fields = ('description',)
    ordering = ('-date',)
    actions = [export_transactions_to_csv]  #custom action

class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'month', 'amount')
    list_filter = ('month', 'category')

class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_amount', 'current_amount', 'deadline')
    list_filter = ('deadline',)
    search_fields = ("name",)

class CustomAdminSite(admin.AdminSite):
    site_header = 'Finance Tracker Admin'
    site_title = 'Finance Tracker'
    index_title = 'Dashboard'

    def index(self, request, extra_content=None):
        """Redirect default admin index to dashboard"""
        return redirect("admin:dashboard")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),]
        return custom_urls + urls

    def dashboard_view(self, request):
        # Total balance per account
        accounts = Account.objects.all()
        balances = {acc.name: acc.balance for acc in accounts}

        #Income vs Expenses Total
        income_total = Transaction.objects.filter(transaction_type='INCOME').aggregate(
            total=Sum('amount'))['total'] or 0
        expense_total = Transaction.objects.filter(transaction_type='EXPENSE').aggregate(
            total=Sum('amount'))['total'] or 0

        context = dict(
            self.each_context(request),
            accounts = balances,
            income = income_total,
            expenses = expense_total,
        )

        # Expenses by Category
        expenses_by_category = (
            Transaction.objects.filter(transaction_type="EXPENSE")
            .values("category__name")
            .annotate(total=Sum("amount"))
        )
        categories = [e["category__name"] for e in expenses_by_category]
        category_totals = [e["total"] for e in expenses_by_category]

        # Monthly Income vs Expenses
        monthly_data = (
            Transaction.objects.annotate(month=TruncMonth("date"))
            .values("month", "transaction_type")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        months = []
        income_series, expense_series = [], []
        for entry in monthly_data:
            month_str = entry["month"].strftime("%Y-%m")
            if month_str not in months:
                months.append(month_str)
            if entry["transaction_type"] == "INCOME":
                income_series.append(entry["total"])
            else:
                expense_series.append(entry["total"])

        context = dict(
            self.each_context(request),
            accounts=balances,
            income=income_total,
            expenses=expense_total,
            categories=categories,
            category_totals=category_totals,
            months=months,
            income_series=income_series,
            expense_series=expense_series,
        )
        return TemplateResponse(request, 'admin/dashboard.html', context)

# Replace default admin site with custom one
custom_admin_site = CustomAdminSite(name="custom_admin")

# Register models under custom admin
custom_admin_site.register(Account, AccountAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Transaction, TransactionAdmin)
custom_admin_site.register(Budget, BudgetAdmin)
custom_admin_site.register(Goal, GoalAdmin)
