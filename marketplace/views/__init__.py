"""
Views package - tách theo từng trang/chức năng để dễ đọc và bảo trì.
urls.py import từ đây, không cần đổi import path.
"""
from .dashboard import (
    save_dashboard_report,
    dashboard_summary,
    dashboard_data,
    dashboard_timeseries,
    admin_notifications,
    export_dashboard_report_csv,
)
from .listings import AdminListingViewSet
from .users import AdminUserViewSet
from .reports import AdminReportViewSet
from .fees import (
    save_fees_report,
    fee_statistics,
    fee_top_transactions,
    export_fees_report_csv,
)
