from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from .models import DailyReport
from .serializers import DailyReportSerializer
from .permissions import REPORT_REVIEWERS, IsReportReviewer,IsReportOwner
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


# Custom Pagination for Daily Reports
class DailyReportPagination(PageNumberPagination):
    page_size = 10              
    page_size_query_param = "page_size"
    max_page_size = 50

# Daily Report Views
class DailyReportCreateView(generics.CreateAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            status="pending"
        )


# Daily Report Views
class MyDailyReportsView(generics.ListAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DailyReportPagination

    def get_queryset(self):
        return DailyReport.objects.filter(
            user=self.request.user
        ).order_by("-report_date")
        
    
# Daily Report Views    
class MyDailyReportUpdateView(generics.UpdateAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated, IsReportOwner]
    queryset = DailyReport.objects.all()

    def perform_update(self, serializer):
        report = self.get_object()
        if report.status != "pending":
            raise PermissionDenied(
                "Approved or rejected reports cannot be edited."
            )
        serializer.save()


# All Daily Reports View for Admins
class AllDailyReportsView(generics.ListAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [IsReportReviewer]
    pagination_class = DailyReportPagination

    def get_queryset(self):
        qs = DailyReport.objects.select_related(
            "user", "reviewed_by"
        )

        status = self.request.query_params.get("status")
        user = self.request.query_params.get("user")
        date = self.request.query_params.get("date")

        if status:
            qs = qs.filter(status=status)
        if user:
            qs = qs.filter(user__id=user)
        if date:
            qs = qs.filter(report_date=date)

        return qs.order_by("-report_date")




# Review Daily Report View for Admins
class ReviewDailyReportView(APIView):
    permission_classes = [IsReportReviewer]

    def patch(self, request, pk):
        report = get_object_or_404(DailyReport, pk=pk)

        status_value = request.data.get("status")
        comment = request.data.get("review_comment", "")

        if status_value not in ["approved", "rejected"]:
            return Response(
                {"error": "Invalid status"},
                status=400
            )

        report.status = status_value
        report.review_comment = comment
        report.reviewed_by = request.user
        report.save()

        serializer = DailyReportSerializer(
            report, context={"request": request}
        )
        return Response(serializer.data)




# Admin Report Stats View
class AdminReportStatsView(APIView):
    permission_classes = [IsReportReviewer]

    def get(self, request):
        today = now()

        qs = DailyReport.objects.all()

        return Response({
            "total": qs.count(),
            "today": qs.filter(report_date=today.date()).count(),
            "this_month": qs.filter(
                report_date__year=today.year,
                report_date__month=today.month
            ).count(),
            "approved": qs.filter(status="approved").count(),
            "pending": qs.filter(status="pending").count(),
            "rejected": qs.filter(status="rejected").count(),
        })



# Report Detail View
class DailyReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        report = get_object_or_404(DailyReport, pk=pk)

        if (
            report.user != request.user and
            request.user.role not in REPORT_REVIEWERS
        ):
            return Response(
                {"error": "Permission denied"},
                status=403
            )

        serializer = DailyReportSerializer(
            report, context={"request": request}
        )
        return Response(serializer.data)

