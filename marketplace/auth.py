from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication nhưng bỏ qua kiểm tra CSRF.

    Chỉ nên dùng cho API nội bộ/admin trong môi trường tin cậy, vì
    sẽ không còn lớp bảo vệ CSRF của Django nữa.
    """

    def enforce_csrf(self, request):
        # Ghi đè để bỏ qua kiểm tra CSRF.
        return None

