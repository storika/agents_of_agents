#!/usr/bin/env python3
"""
Trend Research Pipeline Scheduler
Runs the pipeline every 3 hours automatically.

Usage:
    python scheduler.py                    # Run with 3-hour interval
    python scheduler.py --interval 2       # Custom interval (hours)
    python scheduler.py --once             # Run once then exit
"""

import sys
import time
import schedule
from datetime import datetime
from pathlib import Path

# Import pipeline
from pipeline import run_pipeline_once
from config import COLLECTION_INTERVAL_HOURS


def run_with_logging():
    """Run pipeline with scheduler logging."""
    print("\n" + "=" * 100)
    print(f"[SCHEDULER] Starting pipeline run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)

    result = run_pipeline_once()

    if result == 0:
        print(f"[SCHEDULER] ✓ Pipeline completed successfully")
    else:
        print(f"[SCHEDULER] ✗ Pipeline failed with exit code {result}")

    next_run = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[SCHEDULER] Next run scheduled in {COLLECTION_INTERVAL_HOURS} hours")
    print("=" * 100)

    return result


def run_scheduler(interval_hours: int = COLLECTION_INTERVAL_HOURS):
    """
    Run the pipeline on a schedule.

    Args:
        interval_hours (int): Hours between each run
    """
    print("=" * 100)
    print(" " * 25 + "TREND RESEARCH PIPELINE - SCHEDULED MODE")
    print("=" * 100)
    print(f"Schedule: Every {interval_hours} hours")
    print(f"Output directory: trend_data/")
    print(f"First run: Immediately")
    print("=" * 100)
    print("\nPress Ctrl+C to stop\n")

    # Run immediately on start
    run_with_logging()

    # Schedule future runs
    schedule.every(interval_hours).hours.do(run_with_logging)

    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n[SCHEDULER] Pipeline scheduler stopped by user.")
        from config import TREND_DATA_DIR
        json_files = list(TREND_DATA_DIR.glob('trending_*.json'))
        print(f"[SCHEDULER] Total trend data files: {len(json_files)}")


def main():
    """Main entry point."""
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    # Parse interval
    interval = COLLECTION_INTERVAL_HOURS
    if "--interval" in sys.argv:
        try:
            idx = sys.argv.index("--interval")
            if len(sys.argv) > idx + 1:
                interval = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            print("Error: --interval requires an integer argument")
            sys.exit(1)

    # Run once or scheduled
    if "--once" in sys.argv:
        exit_code = run_pipeline_once()
        sys.exit(exit_code)
    else:
        run_scheduler(interval_hours=interval)


if __name__ == "__main__":
    main()
