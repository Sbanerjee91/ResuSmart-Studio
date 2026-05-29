import os
import sys
from django.core.wsgi import get_wsgi_application

# 📁 Injects your path coordinates into python runtime memory arrays
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'build.settings')

application = get_wsgi_application()

# 🎯 Essential hook variable mapping for Vercel Serverless Functions
app = application
