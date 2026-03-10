"""
Thống kê phí sàn (Fees) - Báo cáo doanh thu và phí sàn từ giao dịch.
- statistics: tổng revenue, phí, tx + theo N ngày (?days=7|14|30)
- top_transactions: 5 giao dịch có phí cao nhất
- save: lưu snapshot báo cáo (report_type=FEES)
"""
from datetime import timedelta

from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import Transaction, AdminReportSnapshot
from ..serializers import TransactionListSerializer


@api_view(['POST'])
@permission_classes([IsAdminUser])
def save_fees_report(request):
    """Lưu báo cáo phí sàn: stats và timeseries vào AdminReportSnapshot."""
    stats_data = request.data.get('stats') or {}
    timeseries_data = request.data.get('timeseries') or {}
    AdminReportSnapshot.objects.create(
        report_type='FEES',
        snapshot_data={'stats': stats_data, 'timeseries': timeseries_data},
        created_by=request.user,
    )
    return Response({'status': 'saved', 'message': 'Đã lưu báo cáo phí sàn.'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def fee_statistics(request):
    """GET ?days=N: Tổng revenue, phí, tx + revenue/phí N ngày gần nhất, phí TB/giao dịch."""
    days = int(request.query_params.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    now = timezone.now()
    since = now - timedelta(days=days)

    summary = Transaction.objects.aggregate(
        total_revenue=Sum('amount'),
        total_platform_fee=Sum('platform_fee'),
        total_transactions=Count('id'),
    )
    last_n = Transaction.objects.filter(created_at__gte=since).aggregate(
        rev=Sum('amount'),
        fee=Sum('platform_fee'),
    )
    rev_n = float(last_n['rev'] or 0)
    fee_n = float(last_n['fee'] or 0)
    cnt = summary['total_transactions'] or 0
    fee_total = summary['total_platform_fee'] or 0
    avg_fee = float(fee_total / cnt) if cnt else 0

    data = {
        'total_revenue': summary['total_revenue'],
        'total_platform_fee': summary['total_platform_fee'],
        'total_transactions': summary['total_transactions'],
        'revenue_last_n_days': rev_n,
        'platform_fee_last_n_days': fee_n,
        'avg_fee_per_transaction': avg_fee,
        'days': days,
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def fee_top_transactions(request):
    """Lấy 5 giao dịch có phí sàn cao nhất."""
    qs = Transaction.objects.select_related('listing', 'buyer').order_by('-platform_fee')[:5]
    serializer = TransactionListSerializer(qs, many=True)
    return Response(serializer.data)
