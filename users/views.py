# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from .permissions import IsManagement, IsSuperAdmin
from leads.models import Lead
from academy.models import Student
from .models import User,ActivityLog
from .serializers import (
    StaffListSerializer,
    StaffDetailSerializer,
    StaffCreateSerializer,
    StaffUpdateSerializer,
    LoginSerializer,
    RegisterSerializer
)


#  Pagination 
class StaffPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


#  Dashboard Stats View
class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            "total_leads": Lead.objects.count(),
            "active_staff": User.objects.filter(is_active=True).count(),
            "total_students": Student.objects.count(),
        }
        return Response(data)


# Recent Activities View
class RecentActivitiesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ActivityLog.objects.all()

        # Role-based visibility
        if request.user.role in ["ADM_EXEC", "TRAINER"]:
            qs = qs.filter(user=request.user)

        activities = qs[:10]

        data = [
            {
                "title": activity.get_activity_type_display(),
                "description": activity.description,
                "time": activity.created_at.strftime("%d %b %Y %I:%M %p"),
            }
            for activity in activities
        ]

        return Response(data)

# Registration View
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


# Login View
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


# Token Refresh View
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


# Logout View
class LogoutAPIView(APIView):
    def post(self, request):
        response = Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )
        response.delete_cookie("refresh_token", path="/api/token/refresh/")
        return response


# Staff List View
class StaffListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = StaffListSerializer
    permission_classes = [IsManagement]
    pagination_class = StaffPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email', 'role', 'phone', 'location']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']



#  Staff Detail View 
class StaffDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsManagement]



#  Staff Create View 
class StaffCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsManagement]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {"message": "Staff created successfully"}
        return response


#  Staff Update View
class StaffUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = StaffUpdateSerializer
    permission_classes = [IsManagement]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"message": "Staff updated successfully"},
            status=status.HTTP_200_OK
        )



#  Staff Delete View 
class StaffDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = StaffDetailSerializer
    permission_classes = [IsSuperAdmin]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"message": "Staff deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class StaffByTeamView(generics.ListAPIView):
    serializer_class = StaffListSerializer
    permission_classes = [IsManagement]
    pagination_class = StaffPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email', 'role', 'phone', 'location', 'team']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_queryset(self):
        queryset = User.objects.filter(is_active=True)
        team = self.request.query_params.get('team')
        if team:
            queryset = queryset.filter(team__iexact=team)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)