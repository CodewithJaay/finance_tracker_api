from django.shortcuts import render

# Create your views here.
from rest_framework import generics, viewsets, permissions
from .models import User, Account, Category, Transaction, Budget
from .serializers import UserSerializer, AccountSerializer, CategorySerializer, TransactionSerializer
from .serializers import BudgetSerializer, DashboardSerializer
from rest_framework.permissions import AllowAny
from django.db.models import Sum 
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response 

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
 
class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #Only return accounts that belong to the logged-in user
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        #Attach the logged-in user automatically
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()
        current_month = today.strftime("%Y-%m")

        # -------------------------
        # AllTimeSummary
        # -------------------------

        total_income = Transaction.objects.filter(user=user, transaction_type='INCOME').aggregate(
            total = Sum('amount')
        )['total'] or 0
        total_expenses = Transaction.objects.filter(user=user, transaction_type='EXPENSE').aggregate(
            total = Sum('amount')
        )['total'] or 0
        net_savings = total_income - total_expenses

        all_time_summary = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': net_savings,
        }

        # -------------------------
        #Current Month Summary
        # -------------------------

        month_income = Transaction.objects.filter(
            user=user, transaction_type='INCOME', date__month=today.month, date__year=today.year).aggregate(
                total = Sum('amount')
            )['total'] or 0
        month_expenses = Transaction.objects.filter(
            user=user, transaction_type='EXPENSE', date__month=today.month, date__year=today.year).aggregate(
                total = Sum('amount')
            )['total'] or 0

        current_month_summary= {
            'month': current_month,
            'income': month_income,
            'expenses': month_expenses,
            'savings': month_income - month_expenses,
        }

        # -------------------------
        #Category Summary (Budget vs Expenditure)
        # -------------------------

        category_summary = []
        categories = Category.objects.filter(user=user)

        for category in categories:
            expenditure = Transaction.objects.filter(
                user=user, category=category, transaction_type='EXPENSE', date__month=today.month, date__year=today.year).aggregate(
                total = Sum('amount')    
                )['total'] or 0
            
            budget_obj = Budget.objects.filter(user=user, category=category, month=current_month).first()

            budget_amount = budget_obj.amount if budget_obj else 0
            balance = budget_amount - expenditure
            status = 'OK'
            if budget_obj and expenditure > budget_amount:
                status = 'Exceeded'

            category_summary.append({
                'category': category.name,
                'expenditure': expenditure,
                'budget': budget_amount,
                'balance': balance,
                'status': status,
            })
        # -------------------------
        #Montly History
        # -------------------------

        transactions_by_month = (
            Transaction.objects.filter(user=user).annotate(month=TruncMonth('date')).values(
                'month', 'transaction_type').annotate(total=Sum('amount')).order_by('month')
            )
            
        monthly_data = {}
        for entry in transactions_by_month:
            month_str = entry['month'].strftime("%Y-%m")
            if month_str not in monthly_data:
                monthly_data[month_str] = {'income':0, 'expenses':0}
            if entry ['transaction_type'] == 'INCOME':
                monthly_data[month_str]["income"] = entry["total"]
            else:
                monthly_data[month_str]["expenses"] = entry["total"]

        monthly_history = []
        for month, data in monthly_data.items():
            monthly_history.append({
                'month': month,
                'income' : data['income'],
                'expenses': data['expenses'],
                'savings' : data['income'] - data['expenses'],
            })

        # -------------------------
        #Serialize Everything
        # -------------------------

        dashboard_data = {
            'all_time_summary' : all_time_summary,
            'current_month_summary' : current_month_summary,
            'category_summary' : category_summary,
            'monthly_history' : monthly_history,
        }

        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data)