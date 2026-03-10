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

from ..models import UserProfile
from ..serializers import UserSerializer


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Khóa tài khoản: đánh dấu UserProfile.is_blocked, User.is_active=False."""
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_blocked = True
        profile.save()
        user.is_active = False
        user.save()
        return Response({'status': 'blocked'})

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        """Mở khóa tài khoản: bỏ chặn và kích hoạt lại user."""
        user = self.get_object()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_blocked = False
        profile.save()
        user.is_active = True
        user.save()
        return Response({'status': 'unblocked'})
