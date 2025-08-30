from rest_framework import serializers
from .models import User
from .models import Account

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
        qs = Account.objects.filter(user=user, name_iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('You already have an account with this name.')
        return value