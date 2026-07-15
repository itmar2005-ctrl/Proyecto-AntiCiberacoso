#!/usr/bin/env python3
"""
Purple Team Framework v2.0 - Launcher
Professional cybersecurity operations platform

Usage:
  python run.py c2 start
  python run.py scan 192.168.1.1
  python run.py --help
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    from purple_team.__main__ import main
    main()
