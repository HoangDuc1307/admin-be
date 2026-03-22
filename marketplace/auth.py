from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication nhưng bỏ qua check CSRF.
    Dùng cho admin/nội bộ thôi vì sẽ mất lớp bảo vệ CSRF gốc.
    """

    def enforce_csrf(self, request):
        # Chặn luôn, khỏi check CSRF
        return None

