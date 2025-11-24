import sys
import asyncio
from .app import TermiDLApp

# Suppress "Event loop is closed" RuntimeError on Windows
if sys.platform == 'win32':
    from asyncio.proactor_events import _ProactorBasePipeTransport
    def silence_event_loop_closed(self, *args):
        pass
    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed

if __name__ == "__main__":
    try:
        app = TermiDLApp()
        app.run()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
