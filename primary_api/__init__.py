import sys
import os

# Ensure the parent directory is included in the module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Optional: Provide project-wide metadata or initialization
__version__ = "1.0.0"
__author__ = "Your Name"
