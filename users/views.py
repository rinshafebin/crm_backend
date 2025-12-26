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
    StaffCreateUpdateSerializer,
    LoginSerializer,
    RegisterSerializer
)


# ---------------- LOGIN VIEW ----------------
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)


# ---------------- REGISTER VIEW ----------------
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)





# ------------------------- Pagination -------------------------
class StaffPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# ------------------------- Staff List View -------------------------

class StaffListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = StaffListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StaffPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email', 'role']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

# ------------------------- Staff Detail View -------------------------

class StaffDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAdminUser]

# ------------------------- Staff Create View -------------------------

class StaffCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffCreateUpdateSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        return Response({
            "message": "Staff created successfully",
            "staff_id": staff.id
        }, status=status.HTTP_201_CREATED)

# ------------------------- Staff Update View -------------------------
class StaffUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffCreateUpdateSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {"message": "Staff updated successfully"}
        return response

# ------------------------- Staff Delete View -------------------------

class StaffDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Staff deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
