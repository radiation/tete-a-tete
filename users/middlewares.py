from django.utils.deprecation import MiddlewareMixin


class LogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"Request received: {request.path}")
        return None
