# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from .models import User
from .serializers import (
    StaffListSerializer,
    StaffDetailSerializer,
    StaffCreateSerializer,
    StaffUpdateSerializer,
    LoginSerializer,
    RegisterSerializer
)


# ------------------------- Pagination -------------------------
class StaffPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100




# ---------------- REGISTER VIEW ----------------


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "Registration successful. Your account is pending admin approval.",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active
            }
        }, status=status.HTTP_201_CREATED)


# ---------------- LOGIN VIEW ----------------

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        
        response = Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,         
            samesite="Lax",
        )
        
        return response


# -- ---------------- REFRESH TOKEN VIEW ----------------

class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response({"access": access_token}, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )


# ------------------------- LOGOUT VIEW  -------------------------

class LogoutAPIView(APIView):
    def post(self, request):
        response = Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )
        response.delete_cookie("refresh_token", path="/api/token/refresh/")
        return response


# ------------------------- Staff List View -------------------------

class StaffListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = StaffListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StaffPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email', 'role', 'phone', 'location']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']


# ------------------------- Staff Detail View -------------------------

class StaffDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAdminUser]

# ------------------------- Staff Create View -------------------------

# views.py

class StaffCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffCreateSerializer  # Use create serializer
    permission_classes = [IsAdminUser]
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {"message": "Staff created successfully"}
        return response


class StaffUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffUpdateSerializer  # Use update serializer
    permission_classes = [IsAdminUser]
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response({"message": "Staff updated successfully"}, status=status.HTTP_200_OK)

# ------------------------- Staff Delete View -------------------------

class StaffDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Staff deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
