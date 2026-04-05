from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .csrf import csrf
from .views import (
    AdminListingViewSet,
    AdminUserViewSet,
    AdminReportViewSet,
    dashboard_summary,
    dashboard_timeseries,
    dashboard_data,
    fee_statistics,
    fee_top_transactions,
    save_dashboard_report,
    save_fees_report,
    export_dashboard_report_csv,
    export_fees_report_csv,
    admin_notifications,
)

router = DefaultRouter()
router.register(r'listings', AdminListingViewSet, basename='admin-listings')
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'reports', AdminReportViewSet, basename='admin-reports')

urlpatterns = [
    path('', include(router.urls)),
    path('csrf/', csrf, name='csrf'),
    path('dashboard/summary/', dashboard_summary, name='dashboard-summary'),
    path('dashboard/timeseries/', dashboard_timeseries, name='dashboard-timeseries'),
    path('dashboard/', dashboard_data, name='dashboard-data'),
    path('dashboard/save-report/', save_dashboard_report, name='save-dashboard-report'),
    path('dashboard/notifications/', admin_notifications, name='admin-notifications'),
    path('dashboard/export-report/', export_dashboard_report_csv, name='export-dashboard-report'),
    path('fees/statistics/', fee_statistics, name='fees-statistics'),
    path('fees/top-transactions/', fee_top_transactions, name='fees-top-transactions'),
    path('fees/save-report/', save_fees_report, name='save-fees-report'),
    path('fees/export-report/', export_fees_report_csv, name='export-fees-report'),
]

