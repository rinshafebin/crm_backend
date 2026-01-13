from django.urls import path
from .views import *

urlpatterns = [

    # Employee
    path("reports/create/", DailyReportCreateView.as_view()),
    path("reports/my/", MyDailyReportsView.as_view()),
    path("reports/<int:pk>/edit/", MyDailyReportUpdateView.as_view()),
    path("reports/<int:pk>/", DailyReportDetailView.as_view(), name="report-detail"),

    # Admin
    path("admin/reports/", AllDailyReportsView.as_view()),
    path("admin/reports/<int:pk>/review/", ReviewDailyReportView.as_view()),
    path("admin/reports/stats/", AdminReportStatsView.as_view()),

]
