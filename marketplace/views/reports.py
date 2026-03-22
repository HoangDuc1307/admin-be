"""
Quản lý báo cáo (Reports) - Admin xử lý khiếu nại từ người dùng.
- GET list: danh sách UserReport
- set_status: POST /id/set_status/ body {status} → OPEN|IN_PROGRESS|RESOLVED|REJECTED
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import UserReport, AdminAuditLog
from ..serializers import UserReportSerializer

class AdminReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserReport.objects.all().order_by('-created_at')
    serializer_class = UserReportSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        # Đổi nhanh trạng thái báo cáo (Open/Resolved/etc.)
        report = self.get_object()
        status_value = request.data.get('status')
        if status_value not in dict(UserReport.REPORT_STATUS):
            return Response({'detail': 'Trạng thái không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
        report.status = status_value
        report.save()
        return Response(UserReportSerializer(report).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        # Xử lý report: Phản hồi + Kỷ luật user (Warn/Block)
        report = self.get_object()
        admin_reply = request.data.get('admin_reply', '')
        resolution_status = request.data.get('status', 'RESOLVED')
        action_type = request.data.get('action') # Các tùy chọn: 'WARN', 'BLOCK', 'NONE'

        # 1. Update status và reply của admin
        report.admin_reply = admin_reply
        report.status = resolution_status
        report.save()

        target_user = report.target_user
        details = f"Đã xử lý báo cáo #{report.id}. Giải quyết: {admin_reply}."

        # 2. Xử phạt phụ thuộc vào lựa chọn của admin
        if action_type == 'WARN':
            profile = target_user.userprofile
            profile.warning_count += 1
            profile.save()
            details += " Hành động: Cảnh cáo người dùng."
        elif action_type == 'BLOCK':
            profile = target_user.userprofile
            profile.is_blocked = True
            profile.save()
            target_user.is_active = False # Vừa khóa profile vừa vô hiệu hóa User của Django
            target_user.save()
            details += " Hành động: Khóa tài khoản vĩnh viễn."

        # 3. Log audit action của admin
        AdminAuditLog.objects.create(
            admin=request.user,
            action='RESOLVE_REPORT',
            details=details,
            target_model="UserReport",
            target_id=str(report.id)
        )

        return Response(UserReportSerializer(report).data)
