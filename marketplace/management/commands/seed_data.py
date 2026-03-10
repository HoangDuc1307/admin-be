"""
Tạo dữ liệu test: users, listings, transactions, reports.
Dùng lệnh: python manage.py seed_data
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from marketplace.models import Listing, Transaction, UserReport, UserProfile


class Command(BaseCommand):
    help = 'Tạo dữ liệu test cho hệ thống (users, listings, transactions, reports)'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Số user cần tạo (mặc định: 10)')
        parser.add_argument('--listings', type=int, default=20, help='Số bài đăng (mặc định: 20)')
        parser.add_argument('--transactions', type=int, default=15, help='Số giao dịch (mặc định: 15)')
        parser.add_argument('--reports', type=int, default=5, help='Số báo cáo vi phạm (mặc định: 5)')
        parser.add_argument('--clear', action='store_true', help='Xóa dữ liệu test cũ trước khi tạo mới')

    def handle(self, *args, **options):
        num_users = options['users']
        num_listings = options['listings']
        num_transactions = options['transactions']
        num_reports = options['reports']

        if options['clear']:
            self.stdout.write('Đang xóa dữ liệu test cũ...')
            Transaction.objects.all().delete()
            UserReport.objects.all().delete()
            Listing.objects.all().delete()
            UserProfile.objects.filter(user__is_superuser=False).delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Đã xóa xong.'))

        # --- Tạo users ---
        first_names = ['Minh', 'Hoa', 'Tuấn', 'Lan', 'Khoa', 'Mai', 'Đức', 'Thảo', 'Hùng', 'Linh',
                        'Nam', 'Ngọc', 'Phúc', 'Trang', 'Bảo', 'Vy', 'Quang', 'Hạnh', 'Dũng', 'Yến']
        last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Đặng', 'Bùi', 'Đỗ', 'Phan']

        users = list(User.objects.filter(is_superuser=False))
        created_count = 0
        for i in range(num_users):
            username = f'user{i + 1}'
            if User.objects.filter(username=username).exists():
                continue
            first = random.choice(first_names)
            last = random.choice(last_names)
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='test1234',
                first_name=first,
                last_name=last,
            )
            UserProfile.objects.get_or_create(user=user)
            users.append(user)
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Đã tạo {created_count} users (tổng: {len(users)} users thường)'))

        if len(users) < 2:
            self.stdout.write(self.style.ERROR('Cần ít nhất 2 user để tạo listings/transactions/reports.'))
            return

        # --- Tạo listings ---
        product_names = [
            'iPhone 15 Pro Max', 'Samsung Galaxy S24', 'Laptop Dell XPS 15', 'iPad Air M2',
            'Tai nghe Sony WH-1000XM5', 'Apple Watch Ultra 2', 'Bàn phím Keychron K8',
            'Màn hình LG UltraWide 34"', 'Chuột Logitech MX Master 3S', 'Loa JBL Flip 6',
            'MacBook Pro M3', 'Nintendo Switch OLED', 'PS5 Slim', 'Xbox Series X',
            'Camera Canon EOS R6', 'Máy ảnh Fujifilm X-T5', 'Đồng hồ Casio G-Shock',
            'Giày Nike Air Max 90', 'Balo Herschel Supply', 'Kính mát Ray-Ban Wayfarer',
            'Nồi chiên không dầu Philips', 'Robot hút bụi Xiaomi', 'Máy lọc không khí Sharp',
            'Tủ lạnh Samsung Inverter', 'Máy giặt LG AI DD',
        ]
        descriptions = [
            'Còn mới 99%, đầy đủ phụ kiện.', 'Mới mua 1 tháng, bảo hành còn dài.',
            'Hàng chính hãng, có hóa đơn.', 'Giá tốt, giao hàng nhanh.',
            'Sử dụng ít, như mới.', 'Fullbox, nguyên seal.', 'Thanh lý giá rẻ.',
        ]
        statuses = ['PENDING', 'APPROVED', 'APPROVED', 'APPROVED', 'REJECTED']  # ưu tiên APPROVED

        listings = list(Listing.objects.all())
        listing_created = 0
        now = timezone.now()
        for i in range(num_listings):
            seller = random.choice(users)
            title = random.choice(product_names)
            listing = Listing.objects.create(
                seller=seller,
                title=f'{title} - #{Listing.objects.count() + 1}',
                description=random.choice(descriptions),
                price=Decimal(random.randint(100, 50000)) * 1000,
                status=random.choice(statuses),
            )
            # Đặt ngày tạo ngẫu nhiên trong 30 ngày qua
            listing.created_at = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            listing.save(update_fields=['created_at'])
            listings.append(listing)
            listing_created += 1

        self.stdout.write(self.style.SUCCESS(f'Đã tạo {listing_created} bài đăng'))

        # --- Tạo transactions ---
        approved_listings = [l for l in listings if l.status == 'APPROVED']
        tx_created = 0
        for i in range(min(num_transactions, len(approved_listings))):
            listing = approved_listings[i]
            buyer = random.choice([u for u in users if u != listing.seller])
            amount = listing.price
            fee = amount * Decimal('0.05')  # Phí sàn 5%
            tx = Transaction.objects.create(
                listing=listing,
                buyer=buyer,
                seller=listing.seller,
                amount=amount,
                platform_fee=fee,
            )
            tx.created_at = listing.created_at + timedelta(hours=random.randint(1, 48))
            tx.save(update_fields=['created_at'])
            tx_created += 1

        self.stdout.write(self.style.SUCCESS(f'Đã tạo {tx_created} giao dịch'))

        # --- Tạo reports ---
        report_reasons = [
            'Bán hàng giả, hàng nhái.', 'Lừa đảo, không giao hàng.',
            'Spam tin nhắn quảng cáo.', 'Ngôn ngữ thô tục, xúc phạm.',
            'Tài khoản giả mạo.', 'Đăng nội dung không phù hợp.',
        ]
        report_statuses = ['OPEN', 'OPEN', 'IN_PROGRESS', 'RESOLVED', 'REJECTED']
        rp_created = 0
        for i in range(num_reports):
            reporter = random.choice(users)
            target = random.choice([u for u in users if u != reporter])
            report = UserReport.objects.create(
                reporter=reporter,
                target_user=target,
                reason=random.choice(report_reasons),
                status=random.choice(report_statuses),
            )
            report.created_at = now - timedelta(days=random.randint(0, 14))
            report.save(update_fields=['created_at'])
            rp_created += 1

        self.stdout.write(self.style.SUCCESS(f'Đã tạo {rp_created} báo cáo vi phạm'))
        self.stdout.write(self.style.SUCCESS('\n✅ Seed data hoàn tất!'))
        self.stdout.write(f'   Tài khoản test: user1 ~ user{num_users} / mật khẩu: test1234')
