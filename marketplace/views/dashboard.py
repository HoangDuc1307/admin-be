"""
Bảng điều khiển (Dashboard) - Thống kê tổng quan hệ thống.
- summary: 6 thẻ số liệu (user, listing, transaction, revenue, ...)
- timeseries: dữ liệu theo ngày cho biểu đồ tăng trưởng
- save: lưu snapshot báo cáo (AdminReportSnapshot)
- export: xuất báo cáo ra file (mở được bằng Excel)
"""
from datetime import timedelta
import csv

from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..models import Listing, Transaction, AdminReportSnapshot


@api_view(['POST'])
@permission_classes([IsAdminUser])
def save_dashboard_report(request):
    """Lưu báo cáo dashboard: summary và timeseries vào AdminReportSnapshot."""
    summary_data = request.data.get('summary') or {}
    timeseries_data = request.data.get('timeseries') or {}
    AdminReportSnapshot.objects.create(
        report_type='DASHBOARD',
        snapshot_data={'summary': summary_data, 'timeseries': timeseries_data},
        created_by=request.user,
    )
    return Response({'status': 'saved', 'message': 'Đã lưu báo cáo dashboard.'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_dashboard_report_csv(request):
    """
    Xuất báo cáo dashboard ra file CSV để tải về (mở bằng Excel).

    File gồm 2 phần:
    - Tổng quan (summary)
    - Dữ liệu theo ngày (timeseries)
    """
    days = int(request.query_params.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    now = timezone.now()
    since = now - timedelta(days=days)
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)

    total_users = User.objects.count()
    total_listings = Listing.objects.count()
    total_transactions = Transaction.objects.count()
    total_revenue = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0
    listings_last_n_days = Listing.objects.filter(created_at__gte=since).count()
    transactions_last_n_days = Transaction.objects.filter(created_at__gte=since).count()

    listings_qs = (
        Listing.objects.filter(created_at__date__gte=start_date)
        .annotate(d=TruncDate('created_at'))
        .values('d')
        .annotate(c=Count('id'))
    )
    txs_qs = (
        Transaction.objects.filter(created_at__date__gte=start_date)
        .annotate(d=TruncDate('created_at'))
        .values('d')
        .annotate(c=Count('id'), revenue=Sum('amount'), fee=Sum('platform_fee'))
    )
    labels = [(start_date + timedelta(days=i)).isoformat() for i in range(days)]
    listing_map = {row['d'].isoformat(): row['c'] for row in listings_qs}
    tx_map = {
        row['d'].isoformat(): {
            'count': row['c'],
            'revenue': float(row['revenue'] or 0),
            'fee': float(row['fee'] or 0),
        }
        for row in txs_qs
    }

    filename = f"dashboard-report-{today.isoformat()}.csv"
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # Phần 1: Summary
    writer.writerow(['BÁO CÁO DASHBOARD'])
    writer.writerow(['Số ngày', days])
    writer.writerow([])
    writer.writerow(['Chỉ số', 'Giá trị'])
    writer.writerow(['Tổng người dùng', total_users])
    writer.writerow(['Tổng bài đăng', total_listings])
    writer.writerow(['Tổng giao dịch', total_transactions])
    writer.writerow(['Tổng doanh thu', float(total_revenue)])
    writer.writerow([f'Bài đăng {days} ngày gần nhất', listings_last_n_days])
    writer.writerow([f'Giao dịch {days} ngày gần nhất', transactions_last_n_days])

    # Phần 2: Timeseries
    writer.writerow([])
    writer.writerow(['DỮ LIỆU THEO NGÀY'])
    writer.writerow(['Ngày', 'Số bài đăng mới', 'Số giao dịch', 'Doanh thu', 'Phí sàn'])
    for label in labels:
        listing_count = listing_map.get(label, 0)
        tx_data = tx_map.get(label, {})
        writer.writerow([
            label,
            listing_count,
            tx_data.get('count', 0),
            tx_data.get('revenue', 0),
            tx_data.get('fee', 0),
        ])

    return response


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_summary(request):
    """Thống kê tổng quan: 6 thẻ (người dùng, bài đăng, giao dịch, doanh thu, bài đăng N ngày, giao dịch N ngày)."""
    days = int(request.query_params.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    now = timezone.now()
    since = now - timedelta(days=days)

    total_users = User.objects.count()
    total_listings = Listing.objects.count()
    total_transactions = Transaction.objects.count()
    total_revenue = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0

    listings_last_n_days = Listing.objects.filter(created_at__gte=since).count()
    transactions_last_n_days = Transaction.objects.filter(created_at__gte=since).count()

    return Response({
        'total_users': total_users,
        'total_listings': total_listings,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'listings_last_n_days': listings_last_n_days,
        'transactions_last_n_days': transactions_last_n_days,
        'days': days,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_data(request):
    """Gộp summary và timeseries trong một request để load nhanh hơn."""
    days = int(request.query_params.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    now = timezone.now()
    since = now - timedelta(days=days)
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)

    total_users = User.objects.count()
    total_listings = Listing.objects.count()
    total_transactions = Transaction.objects.count()
    total_revenue = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0
    listings_last_n_days = Listing.objects.filter(created_at__gte=since).count()
    transactions_last_n_days = Transaction.objects.filter(created_at__gte=since).count()

    labels = [(start_date + timedelta(days=i)).isoformat() for i in range(days)]
    listings_qs = (
        Listing.objects.filter(created_at__date__gte=start_date)
        .annotate(d=TruncDate('created_at'))
        .values('d')
        .annotate(c=Count('id'))
    )
    txs_qs = (
        Transaction.objects.filter(created_at__date__gte=start_date)
        .annotate(d=TruncDate('created_at'))
        .values('d')
        .annotate(c=Count('id'), revenue=Sum('amount'), fee=Sum('platform_fee'))
    )
    listing_map = {row['d'].isoformat(): row['c'] for row in listings_qs}
    tx_map = {
        row['d'].isoformat(): {
            'count': row['c'],
            'revenue': float(row['revenue'] or 0),
            'fee': float(row['fee'] or 0),
        }
        for row in txs_qs
    }

    return Response({
        'summary': {
            'total_users': total_users,
            'total_listings': total_listings,
            'total_transactions': total_transactions,
            'total_revenue': total_revenue,
            'listings_last_n_days': listings_last_n_days,
            'transactions_last_n_days': transactions_last_n_days,
            'days': days,
        },
        'timeseries': {
            'labels': labels,
            'listings_created': [listing_map.get(d, 0) for d in labels],
            'transactions_count': [tx_map.get(d, {}).get('count', 0) for d in labels],
            'revenue': [tx_map.get(d, {}).get('revenue', 0) for d in labels],
            'platform_fee': [tx_map.get(d, {}).get('fee', 0) for d in labels],
        },
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_timeseries(request):
    """Dữ liệu theo ngày cho biểu đồ: số bài đăng mới, giao dịch, doanh thu, phí sàn mỗi ngày."""
    days = int(request.query_params.get('days', 7))
    if days < 1:
        days = 7
    if days > 90:
        days = 90

    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)
    labels = [(start_date + timedelta(days=i)).isoformat() for i in range(days)]

    listings = (
        Listing.objects.filter(created_at__date__gte=start_date)
        .annotate(d=TruncDate('created_at'))
        .values('d')
        .annotate(c=Count('id'))
    )
    txs = (
        Transaction.objects.filter(created_at__date__gte=start_date)
        .annotate(d=TruncDate('created_at'))
        .values('d')
        .annotate(c=Count('id'), revenue=Sum('amount'), fee=Sum('platform_fee'))
    )

    listing_map = {row['d'].isoformat(): row['c'] for row in listings}
    tx_map = {
        row['d'].isoformat(): {
            'count': row['c'],
            'revenue': float(row['revenue'] or 0),
            'fee': float(row['fee'] or 0),
        }
        for row in txs
    }

    return Response({
        'labels': labels,
        'listings_created': [listing_map.get(d, 0) for d in labels],
        'transactions_count': [tx_map.get(d, {}).get('count', 0) for d in labels],
        'revenue': [tx_map.get(d, {}).get('revenue', 0) for d in labels],
        'platform_fee': [tx_map.get(d, {}).get('fee', 0) for d in labels],
    })
