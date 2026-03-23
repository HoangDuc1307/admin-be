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

# Quản lý người dùng - Lọc bớt Admin/Staff ra cho đỡ vướng mắt, tránh khóa nhầm đồng nghiệp
class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False, is_staff=False).order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def block(self, request, pk=None):
        # Khóa tài khoản kèm lý do cụ thể
        user = self.get_object()
        reason = request.data.get('reason', 'Không có lý do cụ thể')
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_blocked = True
        profile.block_reason = reason
        profile.save()
        
        user.is_active = False
        user.save()
 
        # Log audit lại cho admin
        AdminAuditLog.objects.create(
            admin=request.user,
            action='BLOCK_USER',
            details=f"Đã khóa tài khoản người dùng @{user.username} (ID: {user.id}). Lý do: {reason}",
            target_model="User",
            target_id=str(user.id)
        )
 
        return Response({'status': 'blocked', 'reason': reason})

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        # Mở khóa lại tài khoản
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_blocked = False
        profile.save()
        user.is_active = True
        user.save()

        # Log audit lại cho admin
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
        # Tổng hợp full lịch sử của user (tin đăng, mua/bán, report) cho admin check
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
