from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import DailyReport
from .serializers import DailyReportSerializer
from rest_framework.views import APIView



class DailyReportCreateView(generics.CreateAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyDailyReportsView(generics.ListAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyReport.objects.filter(user=self.request.user)


class AllDailyReportsView(generics.ListAPIView):
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        status = self.request.query_params.get("status")
        qs = DailyReport.objects.all()
        if status:
            qs = qs.filter(status=status)
        return qs



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

        return Response({"message": "Report updated successfully"})
