#!/usr/bin/env python3
"""
Purple Team Framework v2.0
Professional cybersecurity operations platform

Usage:
  py run_purple_team.py c2 start
  py run_purple_team.py scan 192.168.1.1
  py run_purple_team.py --help
"""

import sys
import os
from pathlib import Path

# Ensure the project root is in sys.path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Remove the script name and pass remaining args
    sys.argv[0] = "purple-team"
    from purple_team.__main__ import main
    main()
