"""
Duyệt bài đăng (Listings) - Admin duyệt hoặc từ chối tin đăng.
- GET list: danh sách bài đăng (?status=PENDING|APPROVED|REJECTED để lọc)
- approve: POST /id/approve/ → status=APPROVED
- reject: POST /id/reject/ → status=REJECTED
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import Listing, AdminAuditLog
from ..serializers import ListingSerializer # Chuyển đổi data bài đăng

# Viewset duyệt tin
class AdminListingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Lọc tin theo status nếu có param, mặc định vẫn theo ID cho dễ nhìn
        status_param = self.request.query_params.get('status')
        qs = Listing.objects.all()
        if status_param:
            qs = qs.filter(status=status_param)
        return qs.order_by('id')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        # Duyệt tin để hiện lên chợ
        listing = self.get_object()
        listing.status = 'APPROVED'
        listing.save()

        # Log lại audit cho admin
        AdminAuditLog.objects.create(
            admin=request.user,
            action='APPROVE_LISTING',
            details=f"Đã duyệt bài đăng '{listing.title}' (ID: {listing.id})",
            target_model="Listing",
            target_id=str(listing.id)
        )

        return Response(ListingSerializer(listing).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        # Từ chối tin vi phạm
        listing = self.get_object()
        reason = request.data.get('reason', 'Không có lý do')
        listing.status = 'REJECTED'
        listing.reject_reason = reason
        listing.save()

        # Log audit kèm lý do từ chối
        AdminAuditLog.objects.create(
            admin=request.user,
            action='REJECT_LISTING',
            details=f"Đã từ chối bài đăng '{listing.title}' (ID: {listing.id}). Lý do: {reason}",
            target_model="Listing",
            target_id=str(listing.id)
        )

        return Response(ListingSerializer(listing).data)
