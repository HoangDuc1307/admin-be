import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from marketplace.models import Listing, UserProfile, Transaction, UserReport, ReportEvidence, ListingImage

class Command(BaseCommand):
    help = 'Nạp dữ liệu mẫu thực tế cho đồ án (Dành cho sinh viên)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Starting sample data setup ---'))

        # Tạo acc admin (pass: admin123)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created Admin: admin / admin123'))

        # Tạo 10 user mẫu
        users = []
        for i in range(1, 11):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={'email': f'user{i}@example.com'}
            )
            if created:
                user.set_password('password123')
                user.save()
                UserProfile.objects.get_or_create(user=user)
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} sample users.'))

        # List tên sản phẩm TV cho thật
        titles = [
            'Laptop Dell Latitude 7490 cu', 'iPhone 13 Pro Max 256GB', 'Tay cam PS5 DualSense', 
            'Ban phim co AKKO 3068', 'Man hinh Dell UltraSharp 24', 'Tai nghe Sony WH-1000XM4',
            'May anh Canon EOS R6', 'Sac du phong Anker 20000mAh', 'Chuot Logitech G502',
            'Loa Bluetooth Marshall Emberton', 'iPad Air 5 M1', 'Sach Clean Code (Tieng Viet)'
        ]

        # Tạo tin đăng mẫu cho đa dạng trạng thái
        listings = []
        for i in range(20):
            title = random.choice(titles) + f" #{i+1}"
            seller = random.choice(users)
            listing = Listing.objects.create(
                seller=seller,
                title=title,
                description=f'Mo ta chi tiet cho san pham {title}. Hang con moi 95%, day du phu kien.',
                price=random.randint(500000, 20000000),
                status=random.choice(['APPROVED', 'PENDING', 'REJECTED']),
                reject_reason='Hinh anh khong ro rang' if i % 5 == 0 else ''
            )
            listings.append(listing)
        self.stdout.write(self.style.SUCCESS(f'Created {len(listings)} listings.'))

        # Tạo vài giao dịch mẫu (chỉ lấy tin đã duyệt)
        for i in range(5):
            listing = random.choice([l for l in listings if l.status == 'APPROVED'])
            buyer = random.choice([u for u in users if u != listing.seller])
            Transaction.objects.create(
                listing=listing,
                buyer=buyer,
                seller=listing.seller,
                amount=listing.price,
                platform_fee=listing.price * 10 / 100
            )
        self.stdout.write(self.style.SUCCESS('Created 5 transactions.'))

        # Tạo report mẫu kèm bằng chứng demo
        for i in range(3):
            reporter = random.choice(users)
            target = random.choice([u for u in users if u != reporter])
            report = UserReport.objects.create(
                reporter=reporter,
                target_user=target,
                reason='Nguoi ban co dau hieu lua dao, khong gui hang.',
                status=random.choice(['OPEN', 'RESOLVED'])
            )
            # Tạo thêm 1-2 minh chứng cho mỗi báo cáo
            for _ in range(random.randint(1, 2)):
                ReportEvidence.objects.create(
                    report=report,
                    # Lưu ý: Trong thực tế sẽ là file ảnh, ở đây ta để trống 
                    # để demo giao diện có hiện phần "Bằng chứng kèm theo"
                )
        self.stdout.write(self.style.SUCCESS('Created 3 reports with evidence records.'))

        self.stdout.write(self.style.SUCCESS('--- SETUP COMPLETE ---'))
