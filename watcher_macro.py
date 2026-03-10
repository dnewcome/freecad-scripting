"""
FreeCAD live-reload watcher macro.

Run this once from the FreeCAD macro editor (Macro > Macros...).
It watches all .py files under the project directory and re-executes
assembly.py (ENTRY_POINT) whenever any of them change.
"""

import os
import traceback
import FreeCAD as App
from PySide2 import QtCore

# ── Configuration ────────────────────────────────────────────────────

PROJECT_DIR  = os.path.dirname(os.path.abspath(__file__))
ENTRY_POINT  = os.path.join(PROJECT_DIR, "assembly.py")
INTERVAL_MS  = 500

# ── State ────────────────────────────────────────────────────────────

_mtimes = {}
_timer  = None


def _scan_py_files():
    """Return {path: mtime} for all .py files in PROJECT_DIR (recursive)."""
    result = {}
    for root, dirs, files in os.walk(PROJECT_DIR):
        # skip hidden dirs / __pycache__
        dirs[:] = [d for d in dirs if not d.startswith((".", "__"))]
        for fname in files:
            if fname.endswith(".py"):
                path = os.path.join(root, fname)
                try:
                    result[path] = os.path.getmtime(path)
                except OSError:
                    pass
    return result


def _run_entry_point():
    try:
        with open(ENTRY_POINT) as f:
            source = f.read()
        exec(compile(source, ENTRY_POINT, "exec"), {"__file__": ENTRY_POINT})
        App.Console.PrintMessage(
            f"[watcher] reloaded {os.path.relpath(ENTRY_POINT, PROJECT_DIR)}\n"
        )
    except Exception:
        App.Console.PrintError("[watcher] error:\n" + traceback.format_exc())


def _check():
    global _mtimes
    current = _scan_py_files()
    changed = [p for p, t in current.items() if _mtimes.get(p) != t]
    if changed:
        for p in changed:
            App.Console.PrintMessage(
                f"[watcher] changed: {os.path.relpath(p, PROJECT_DIR)}\n"
            )
        _mtimes = current
        _run_entry_point()


# ── Start ─────────────────────────────────────────────────────────────

# Stop any previously running timer (handles both old and new variable names)
for _old_timer_name in ("_timer", "_watcher_timer"):
    try:
        _t = vars().get(_old_timer_name) or globals().get(_old_timer_name)
        if _t is not None:
            _t.stop()
    except Exception:
        pass

_watcher_timer = QtCore.QTimer()
_watcher_timer.timeout.connect(_check)
_watcher_timer.start(INTERVAL_MS)

_mtimes = _scan_py_files()   # snapshot so first check doesn't re-fire everything

App.Console.PrintMessage(
    f"[watcher] watching {PROJECT_DIR} (entry: assembly.py, every {INTERVAL_MS}ms)\n"
)

# Run immediately on macro start
_run_entry_point()
