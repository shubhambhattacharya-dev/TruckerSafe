import time, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime, timezone
from apps.routing.api.views import plan_routes

t0 = time.time()
plan = plan_routes(
    origin='Dallas, TX',
    destination='Nashville, TN',
    departure_time=datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc),
    load_lb=40000,
    checkpoint_interval_miles=10
)
t1 = time.time()
print(f"Total time with 10 miles: {t1 - t0:.2f}s")
