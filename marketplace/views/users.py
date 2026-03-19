"""
Quản lý tài khoản (Users) - Admin khóa/mở khóa user.
- block: POST /id/block/ → UserProfile.is_blocked=True, User.is_active=False
- unblock: POST /id/unblock/ → đảo ngược
"""
from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import UserProfile, AdminAuditLog, Listing, Transaction, UserReport
from ..serializers import UserSerializer, ListingSerializer, TransactionListSerializer, UserReportSerializer

# ViewSet quản lý người dùng
class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Hàm thực hiện khóa tài khoản người dùng."""
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_blocked = True
        profile.save()
        user.is_active = False
        user.save()

        # Lưu vết hành động khóa user
        AdminAuditLog.objects.create(
            admin=request.user,
            action='BLOCK_USER',
            details=f"Đã khóa tài khoản người dùng @{user.username} (ID: {user.id})",
            target_model="User",
            target_id=str(user.id)
        )

        return Response({'status': 'blocked'})

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Hàm thực hiện mở khóa lại tài khoản."""
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_blocked = False
        profile.save()
        user.is_active = True
        user.save()

        # Lưu vết hành động mở khóa
        AdminAuditLog.objects.create(
            admin=request.user,
            action='UNBLOCK_USER',
            details=f"Đã mở khóa tài khoản người dùng @{user.username} (ID: {user.id})",
            target_model="User",
            target_id=str(user.id)
        )

        return Response({'status': 'unblocked'})

    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        """
        API tổng hợp toàn bộ lịch sử hoạt động của một User để Admin tiện theo dõi:
        - Danh sách bài đăng.
        - Lịch sử mua hàng / bán hàng.
        - Các báo cáo vi phạm liên quan.
        """
        user = self.get_object()
        listings = Listing.objects.filter(seller=user).order_by('-created_at')
        purchases = Transaction.objects.filter(buyer=user).order_by('-created_at')
        sales = Transaction.objects.filter(seller=user).order_by('-created_at')
        reports_made = UserReport.objects.filter(reporter=user).order_by('-created_at')
        reports_received = UserReport.objects.filter(target_user=user).order_by('-created_at')

        data = {
            'user': UserSerializer(user).data,
            'listings': ListingSerializer(listings, many=True).data,
            'purchases': TransactionListSerializer(purchases, many=True).data,
            'sales': TransactionListSerializer(sales, many=True).data,
            'reports_made': UserReportSerializer(reports_made, many=True).data,
            'reports_received': UserReportSerializer(reports_received, many=True).data,
        }
        return Response(data)
