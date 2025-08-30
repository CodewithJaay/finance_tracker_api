from django.shortcuts import render

# Create your views here.
from rest_framework import generics, viewsets, permissions
from .models import User, Account
from .serializers import UserSerializer, AccountSerializer
from rest_framework.permissions import AllowAny

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