from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Listing, UserReport, Transaction, UserProfile, ReportEvidence, ListingImage


# Xử lý ảnh bài đăng
class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'uploaded_at']


# Chuyển đổi thông tin bài đăng để Admin duyệt
class ListingSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'status', 
            'seller_username', 'reject_reason', 'images', 'created_at'
        ]


# Thông tin User - Gom cả số gậy (cảnh báo) và lý do khóa từ Profile vào cho dễ quản lý
class UserSerializer(serializers.ModelSerializer):
    is_blocked = serializers.SerializerMethodField()
    warning_count = serializers.IntegerField(source='userprofile.warning_count', read_only=True)
    block_reason = serializers.CharField(source='userprofile.block_reason', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_blocked', 'date_joined', 'warning_count', 'block_reason']

    def get_is_blocked(self, obj):
        try:
            return obj.userprofile.is_blocked
        except UserProfile.DoesNotExist:
            return False


# Xử lý ảnh bằng chứng trong báo cáo
class ReportEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEvidence
        fields = ['id', 'image', 'uploaded_at']

# Đổ dữ liệu tố cáo người dùng
class UserReportSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)
    target_username = serializers.CharField(source='target_user.username', read_only=True)
    reporter_id = serializers.IntegerField(source='reporter.id', read_only=True)
    target_id = serializers.IntegerField(source='target_user.id', read_only=True)
    evidences = ReportEvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = UserReport
        fields = [
            'id', 'reporter_id', 'reporter_username', 'target_id', 'target_username', 
            'reason', 'admin_reply', 'status', 'evidences', 'created_at', 'updated_at'
        ]


# Gom nhóm số liệu tổng quan về phí sàn
class TransactionFeeSummarySerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_platform_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()


# Chi tiết từng giao dịch để hiện lên bảng hoặc xuất file Excel
class TransactionListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    platform_fee = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)

