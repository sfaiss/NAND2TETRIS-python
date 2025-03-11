"""Adding project directory to sys.path for easier imports."""

import pathlib
import sys

script_dir = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir.parent))
