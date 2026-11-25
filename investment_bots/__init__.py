"""Paper-only NSE cash investment portfolios, isolated from the F&O workers."""
from pathlib import Path
import sys

# The application is launched as app.main from backend; command-line research
# import/verification entry points must resolve that same service namespace.
_backend = str(Path(__file__).resolve().parents[1] / 'backend')
if _backend not in sys.path:
    sys.path.insert(0, _backend)
