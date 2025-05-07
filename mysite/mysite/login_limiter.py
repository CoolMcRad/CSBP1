from django.core.cache import cache
from django.http import HttpResponse
import time

MAX_ATTEMPTS = 5  # Max attempts
LOCKOUT_TIME = 300  # Lockout time in seconds
ATTEMPT_WINDOW = 60  # Time window for attempts in seconds


def limit_login_rate(get_response):
    def middleware(request):
        if request.path.startswith("/admin/login/"):
            ip = request.META.get("REMOTE_ADDR")
            cache_key = f"login_attempts_{ip}"
            attempts = cache.get(cache_key, {"count": 0, "timestamp": time.time()})
            
            print(f"Login attempts for {ip}: {attempts}")

            if attempts["count"] >= MAX_ATTEMPTS:
                if time.time() - attempts["timestamp"] < LOCKOUT_TIME:
                    return HttpResponse(
                        "Too many failed login attempts. Try again later.", status=429
                    )

            response = get_response(request)
            
            print(f"Response status code: {response.status_code}")

            if response.status_code == 200:
                attempts["count"] += 1
                attempts["timestamp"] = time.time()
                cache.set(cache_key, attempts, ATTEMPT_WINDOW)

            return response
        return get_response(request)

    return middleware
