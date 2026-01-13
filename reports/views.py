from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from .models import DailyReport
from .serializers import DailyReportSerializer
from .permissions import IsOwner


class DailyReportCreateView(generics.CreateAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            status="pending"
        )


class MyDailyReportsView(generics.ListAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyReport.objects.filter(
            user=self.request.user
        ).order_by("-report_date")
        
        
class MyDailyReportUpdateView(generics.UpdateAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = DailyReport.objects.all()

    def perform_update(self, serializer):
        report = self.get_object()
        if report.status != "pending":
            raise PermissionError("Approved or rejected reports cannot be edited")
        serializer.save()



class AllDailyReportsView(generics.ListAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = DailyReport.objects.select_related("user", "reviewed_by")

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




class ReviewDailyReportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            report = DailyReport.objects.get(pk=pk)
        except DailyReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        status_value = request.data.get("status")
        comment = request.data.get("review_comment", "")

        if status_value not in ["approved", "rejected"]:
            return Response({"error": "Invalid status"}, status=400)

        report.status = status_value
        report.review_comment = comment
        report.reviewed_by = request.user
        report.save()

        return Response(DailyReportSerializer(report, context={"request": request}).data)




class AdminReportStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

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




class DailyReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            report = DailyReport.objects.get(pk=pk)
        except DailyReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)
        if not request.user.is_staff and report.user != request.user:
            return Response({"error": "You do not have permission to view this report"}, status=403)

        serializer = DailyReportSerializer(report, context={"request": request})
        return Response(serializer.data)
