from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework import serializers

from ..models import AdminAuditLog

class AdminAuditLogSerializer(serializers.ModelSerializer):
    admin_username = serializers.CharField(source='admin.username', read_only=True)
    target_object = serializers.SerializerMethodField()

    class Meta:
        model = AdminAuditLog
        fields = ['id', 'admin_username', 'action', 'details', 'target_object', 'timestamp']

    def get_target_object(self, obj):
        if obj.content_object:
            return str(obj.content_object)
        return "Unknown"

class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API cung cấp nhật ký hoạt động của Admin.
    Hỗ trợ filter theo `action`.
    """
    queryset = AdminAuditLog.objects.all().order_by('-timestamp')
    serializer_class = AdminAuditLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        action_param = self.request.query_params.get('action')
        if action_param:
            qs = qs.filter(action=action_param)
        return qs
