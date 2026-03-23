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

        # Log audit action
        AdminAuditLog.objects.create(
            admin=request.user,
            action='UPDATE_REPORT_STATUS',
            details=f"Đã chuyển trạng thái báo cáo #{report.id} sang {status_value}.",
            target_model="UserReport",
            target_id=str(report.id)
        )
        return Response(UserReportSerializer(report).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Xử lý báo cáo: Phản hồi nhanh, tự động cảnh báo hoặc khóa luôn nếu cần.
        """
        report = self.get_object()
        admin_reply = request.data.get('admin_reply', '')
        resolution_status = request.data.get('status', 'RESOLVED')
        action_type = request.data.get('action', 'NONE')

        # Giữ lại trạng thái cũ để check, tránh trường hợp admin ấn giải quyết nhiều lần gây cộng dồn gậy
        old_status = report.status
        report.admin_reply = admin_reply
        report.status = resolution_status
        report.save()

        target_user = report.target_user
        profile = target_user.userprofile
        details = f"Đã xong báo cáo #{report.id} ({resolution_status}). Note: {admin_reply}."

        # Nếu tố cáo chuẩn (RESOLVED) thì tự động tặng 1 gậy cảnh báo cho user
        if resolution_status == 'RESOLVED' and old_status != 'RESOLVED':
            profile.warning_count += 1
            details += " (Hệ thống tự động +1 cảnh báo)"
        
        # Tiện tay khóa vĩnh viễn luôn nếu admin tích chọn
        if action_type == 'BLOCK':
            profile.is_blocked = True
            target_user.is_active = False # Chặn đăng nhập luôn cho chắc
            target_user.save()
            details += " -> Đã khóa tài khoản."
        
        profile.save() # Lưu lại các thay đổi của profile (gậy, trạng thái khóa)

        # Lưu log để sau này còn biết ai là người "ra tay" xử lý cái report này
        AdminAuditLog.objects.create(
            admin=request.user,
            action='RESOLVE_REPORT',
            details=details,
            target_model="UserReport",
            target_id=str(report.id)
        )

        return Response(UserReportSerializer(report).data)
