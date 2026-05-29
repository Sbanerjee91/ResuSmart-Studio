import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# 1. Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 2. Set the environment variable for your settings module explicitly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'build.settings')

# 3. Force Django to initialize its application registry first
django.setup()

# 4. Expose the WSGI application for Vercel
application = get_wsgi_application()
app = application
