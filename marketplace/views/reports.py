"""
Quản lý báo cáo (Reports) - Admin xử lý khiếu nại từ người dùng.
- GET list: danh sách UserReport
- set_status: POST /id/set_status/ body {status} → OPEN|IN_PROGRESS|RESOLVED|REJECTED
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import UserReport
from ..serializers import UserReportSerializer


class AdminReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserReport.objects.all().order_by('-created_at')
    serializer_class = UserReportSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        """Đổi trạng thái báo cáo (Mở, Đang xử lý, Đã giải quyết, Từ chối)."""
        report = self.get_object()
        status_value = request.data.get('status')
        if status_value not in dict(UserReport.REPORT_STATUS):
            return Response({'detail': 'Trạng thái không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
        report.status = status_value
        report.save()
        return Response(UserReportSerializer(report).data)
