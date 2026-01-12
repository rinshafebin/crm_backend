from django.urls import path
from .views import (
    DailyReportCreateView,
    MyDailyReportsView,
    AllDailyReportsView,
    ReviewDailyReportView,
)

urlpatterns = [
    path("reports/create/", DailyReportCreateView.as_view()),
    path("reports/my/", MyDailyReportsView.as_view()),
    path("reports/all/", AllDailyReportsView.as_view()),
    path("reports/<int:pk>/review/", ReviewDailyReportView.as_view()),
]
