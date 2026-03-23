"""
Duyệt bài đăng (Listings) - Cho phép Admin duyệt hoặc bác bỏ tin đăng của người dùng.
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import Listing, AdminAuditLog
from ..serializers import ListingSerializer

# Xử lý duyệt tin của admin
class AdminListingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Lọc nhanh theo trạng thái (Duyệt/Chờ/Từ chối) nếu truyền param lên
        status_param = self.request.query_params.get('status')
        qs = Listing.objects.all()
        if status_param:
            qs = qs.filter(status=status_param)
        return qs.order_by('id')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        # Duyệt xong là tin được đẩy lên chợ luôn
        listing = self.get_object()
        listing.status = 'APPROVED'
        listing.save()

        # Lưu lại nhật ký để sau này biết ai đã duyệt cái tin này
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
        # Từ chối nếu tin vi phạm quy định, bắt buộc phải có lý do gửi cho chủ tin
        listing = self.get_object()
        reason = request.data.get('reason', 'Không có lý do cụ thể')
        listing.status = 'REJECTED'
        listing.reject_reason = reason
        listing.save()

        # Log audit kèm lý do từ chối để đối soát khi cần
        AdminAuditLog.objects.create(
            admin=request.user,
            action='REJECT_LISTING',
            details=f"Đã từ chối bài đăng '{listing.title}' (ID: {listing.id}). Lý do: {reason}",
            target_model="Listing",
            target_id=str(listing.id)
        )

        return Response(ListingSerializer(listing).data)
