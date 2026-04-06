import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from shared.python.events_lib.base import EventPublisher

publisher = EventPublisher()
