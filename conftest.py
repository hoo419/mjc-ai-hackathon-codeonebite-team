import sys
from pathlib import Path

# Add backend directory to path so tests can import from 'app' and 'backend.scripts'
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
