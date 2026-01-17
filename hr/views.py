from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Penalty, AttendanceDocument
from .serializers import PenaltySerializer, AttendanceDocumentSerializer
from .permissions import IsHR

User = get_user_model()

#  Penalty APIs 

class PenaltyListCreateAPI(APIView):
    permission_classes = [IsHR]

    def get(self, request):
        penalties = Penalty.objects.all()
        month = request.GET.get("month")
        user_id = request.GET.get("user")

        if month:
            penalties = penalties.filter(month=month)
        if user_id:
            penalties = penalties.filter(user_id=user_id)

        serializer = PenaltySerializer(penalties.order_by("-date"), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PenaltySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class PenaltyDetailAPI(APIView):
    permission_classes = [IsHR]

    def put(self, request, pk):
        try:
            penalty = Penalty.objects.get(pk=pk)
        except Penalty.DoesNotExist:
            return Response({"error": "Penalty not found"}, status=404)

        serializer = PenaltySerializer(penalty, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            penalty = Penalty.objects.get(pk=pk)
        except Penalty.DoesNotExist:
            return Response({"error": "Penalty not found"}, status=404)

        penalty.delete()
        return Response({"message": "Penalty deleted"})


#  Attendance APIs 
class AttendanceDocumentAPI(APIView):
    permission_classes = [IsHR]

    def get(self, request):
        docs = AttendanceDocument.objects.all()
        month = request.GET.get("month")

        if month:
            docs = docs.filter(month=month)

        serializer = AttendanceDocumentSerializer(docs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AttendanceDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# Attendance Document Delete API
class AttendanceDocumentDeleteAPI(APIView):
    permission_classes = [IsHR]

    def delete(self, request, pk):
        try:
            doc = AttendanceDocument.objects.get(pk=pk)
        except AttendanceDocument.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

        doc.delete()
        return Response({"message": "Document deleted"})
