import sys
from pathlib import Path

# Make `import api` and `import src...` work however pytest is started.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
