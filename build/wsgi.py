import os
import sys
from django.core.wsgi import get_wsgi_application

# 1. Get the absolute path of the directory containing wsgi.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the main project root directory path
project_root = os.path.dirname(current_dir)

# 3. Force append both paths directly into Python's module search pathways
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 4. Bind the environment settings module definition safely
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'build.settings')

# 5. Initialize the standard WSGI handler application targets
application = get_wsgi_application()
app = application
