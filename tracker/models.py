from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from decimal import Decimal

class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Account(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
        db_index=True
    )

    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_type = models.CharField(max_length=100, choices=[
        ('cash', 'Cash'),
        ('bank','Bank'),
        ('mobile_money', 'Mobile Money'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other'),
        ],
        default='cash'
    )

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.email})"

class Category(models.Model):
    CATEGORY_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category_type})"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.category.name})"

class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'category', 'month')

    def __str__(self):
        return f"{self.user.name} - {self.category.name} ({self.month}) : {self.amount}"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    name = models.CharField(max_length=200)  # e.g., "Car"
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def progress(self):
        return (self.current_amount / self.target_amount) * 100 if self.target_amount else 0

    def __str__(self):
        return self.name
