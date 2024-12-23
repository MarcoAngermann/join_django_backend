from rest_framework import generics
from .serializers import CustomUserSerializer, UserRegisterSerializer
from ..models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import EmailAuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

class CustomerUserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CustomerUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class CurrentUser(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class RegisterView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
        else:
            print("Registration errors:", serializer.errors)
            data = serializer.errors
        return Response(data)

class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Request received with data:", request.data)
        serializer = EmailAuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            print("User authenticated:", user)

            if not user.is_active:
                return Response({"error": "User account is inactive."}, status=status.HTTP_403_FORBIDDEN)

            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            data = {
                'token': token.key,
                'email': user.email,
            }
            return Response(data, status=status.HTTP_200_OK)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=400)

class GuestLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        guest_user, created = CustomUser.objects.get_or_create(
            email='guest@guest.com',
            defaults={'username': 'GuestUser', 'is_guest': True}
        )

        if not guest_user.is_active:
            return Response({"error": "Guest account is inactive."}, status=status.HTTP_403_FORBIDDEN)

        Token.objects.filter(user=guest_user).delete()
        token = Token.objects.create(user=guest_user)
        data = {
            'token': token.key,
            'email': guest_user.email,
        }
        return Response(data, status=status.HTTP_200_OK)