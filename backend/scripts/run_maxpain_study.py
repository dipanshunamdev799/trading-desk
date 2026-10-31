"""Run the real one-year study; all successful source data is durably cached."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]
from app.config import get_settings
from app.services.maxpain_study import run_study

if __name__ == "__main__":
    run_study(get_settings().backtests_dir, ROOT / "artifacts" / "maxpain-study-progress.json")
