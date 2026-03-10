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

from ..models import Listing
from ..serializers import ListingSerializer


class AdminListingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Listing.objects.all().order_by('-created_at')
    serializer_class = ListingSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Lấy danh sách bài đăng, sắp xếp theo `id` kể cả khi lọc.

        Trước đây chỉ sắp xếp theo id khi không có status, còn khi lọc theo
        trạng thái thì dùng `-created_at`. Người dùng muốn tất cả các tab –
        chờ duyệt/đã duyệt/từ chối – cũng đều theo id, vì vậy ta bỏ luôn
        ordering theo created_at.
        """
        status_param = self.request.query_params.get('status')
        qs = Listing.objects.all()
        if status_param:
            qs = qs.filter(status=status_param)
        # regardless of filter, sort by id ascending
        return qs.order_by('id')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        listing = self.get_object()
        listing.status = 'APPROVED'
        listing.save()
        return Response(ListingSerializer(listing).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Từ chối bài đăng: chuyển trạng thái sang Từ chối."""
        listing = self.get_object()
        listing.status = 'REJECTED'
        listing.save()
        return Response(ListingSerializer(listing).data)
