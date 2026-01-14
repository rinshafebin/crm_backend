from rest_framework import serializers
from .models import DailyReport

#  Daily Report Serializer
class DailyReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    file_url = serializers.SerializerMethodField()
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model = DailyReport
        fields = [
            "id",
            "user",
            "user_name",
            "name",
            "heading",
            "report_text",
            "attached_file",
            "file_url",
            "report_date",
            "status",
            "review_comment",
            "reviewed_by",
            "reviewed_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "status",
            "reviewed_by",
            "review_comment",
            "created_at",
            "updated_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.attached_file and request:
            return request.build_absolute_uri(obj.attached_file.url)
        return None
