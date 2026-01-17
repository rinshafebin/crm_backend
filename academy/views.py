from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import csv
from .models import Trainer, Student, Attendance
from .serializers import TrainerSerializer, StudentSerializer, AttendanceSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
# Custom paginator
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class TrainerListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trainers = Trainer.objects.select_related('user').all()
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(trainers, request)
        serializer = TrainerSerializer(page, many=True)
        print(serializer.data)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TrainerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainerDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        trainer = get_object_or_404(Trainer, pk=pk)
        serializer = TrainerSerializer(trainer)
        return Response(serializer.data)

    def put(self, request, pk):
        trainer = get_object_or_404(Trainer, pk=pk)
        serializer = TrainerSerializer(trainer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        trainer = get_object_or_404(Trainer, pk=pk)
        trainer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class StudentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = Student.objects.select_related('trainer', 'trainer__user').all()
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(students, request)
        serializer = StudentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AttendanceListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = Attendance.objects.select_related('student', 'trainer', 'trainer__user').all()
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(records, request)
        serializer = AttendanceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AttendanceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.GET.get('student')
        trainer_id = request.GET.get('trainer')
        date = request.GET.get('date')

        records = Attendance.objects.select_related('student', 'trainer', 'trainer__user')

        if student_id:
            records = records.filter(student_id=student_id)
        if trainer_id:
            records = records.filter(trainer_id=trainer_id)
        if date:
            records = records.filter(date=date)

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(records, request)
        serializer = AttendanceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class QuickMarkAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'trainer_profile'):
            return Response(
                {"error": "Only trainers can mark attendance"},
                status=status.HTTP_403_FORBIDDEN
            )

        trainer = request.user.trainer_profile
        date = request.data.get('date')
        records = request.data.get('records', [])

        if not date or not records:
            return Response(
                {"error": "date and records are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        saved_records = []

        for r in records:
            attendance, _ = Attendance.objects.update_or_create(
                trainer=trainer,
                student_id=r.get('student'),
                date=date,
                defaults={'status': r.get('status', 'PRESENT')}
            )
            saved_records.append(attendance)

        serializer = AttendanceSerializer(saved_records, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class AttendanceRecordsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        records = Attendance.objects.filter(student_id=student_id).select_related('trainer')
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(records, request)
        serializer = AttendanceSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ExportStudentAttendanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        records = Attendance.objects.filter(student_id=student_id).select_related('trainer')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="student_{student_id}_attendance.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Trainer', 'Status'])

        for r in records:
            writer.writerow([r.date, r.trainer.user.get_full_name(), r.status])

        return response




class StudentStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_students = Student.objects.count()

        status_counts = (
            Student.objects
            .values('status')
            .annotate(count=Count('id'))
        )

        # Default values
        stats = {
            "total": total_students,
            "ACTIVE": 0,
            "COMPLETED": 0,
            "PAUSED": 0,
            "DROPPED": 0,
        }

        for item in status_counts:
            stats[item['status']] = item['count']

        # Combine PAUSED + DROPPED if frontend needs it
        stats["PAUSED_DROPPED"] = stats["PAUSED"] + stats["DROPPED"]

        return Response(stats)
