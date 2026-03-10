from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Listing, UserReport, Transaction, UserProfile


class ListingSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'status', 'seller_username', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    is_blocked = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_blocked', 'date_joined']

    def get_is_blocked(self, obj):
        try:
            return obj.userprofile.is_blocked
        except UserProfile.DoesNotExist:
            return False


class UserReportSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)
    target_username = serializers.CharField(source='target_user.username', read_only=True)

    class Meta:
        model = UserReport
        fields = ['id', 'reporter_username', 'target_username', 'reason', 'status', 'created_at', 'updated_at']


class TransactionFeeSummarySerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_platform_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_transactions = serializers.IntegerField()


class TransactionListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    platform_fee = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)

