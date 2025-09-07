import bleach
from rest_framework import serializers
from .models import User
from .models import Account
from .models import Category, Transaction, Budget, Goal

ALLOWED_TAGS = []   # no HTML tags allowed
ALLOWED_ATTRS = {}  # no HTML attributes allowed

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ['id', 'username', 'email', 'date_joined']

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """
        Ensure the user doesn't have an account with the same name (case-insensitive).
        """
        user = self.context['request'].user
        qs = Account.objects.filter(user=user, name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('You already have an account with this name.')
        return value

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'currency', 'description', 'date', 'category', 'category_name',
        'account', 'account_name', 'created_at']

    def validate_description(self, value):
        # Strip HTML/JS input to prevent XSS
        return bleach.clean(value or "", tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

    def validate(self, data):
        user = self.context['request'].user
        category = data['category']
        date = ['date']
        month = date.strftime('%Y-%m')
        qs = Budget.objects.filter(user=user, category=category, month=month)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Budget already exists for this category and month.")
        return data

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'month', 'amount']
        read_only_fields = ['user']

class GoalSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ['id', 'name', 'target_amount', 'current_amount', 'deadline', 'created_at', 'progress']

    def get_progress(self, obj):
        return obj.progress()

# Dashboard Serializers
class AllTimeSummarySerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_savings = serializers.DecimalField(max_digits=12, decimal_places=2)

class CurrentMonthSummarySerializer(serializers.Serializer):
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    savings = serializers.DecimalField(max_digits=12, decimal_places=2)

class CategorySummarySerializer(serializers.Serializer):
    category = serializers.CharField()
    expenditure = serializers.DecimalField(max_digits=12, decimal_places=2)
    budget = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField()

class MonthlyHistorySerializer(serializers.Serializer):
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    savings = serializers.DecimalField(max_digits=12, decimal_places=2)

class DashboardSerializer(serializers.Serializer):
    all_time_summary = AllTimeSummarySerializer()
    current_month_summary = CurrentMonthSummarySerializer()
    category_summary = CategorySummarySerializer(many=True)
    monthly_history = MonthlyHistorySerializer(many=True)
    

