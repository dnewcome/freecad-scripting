"""
Assembly entry point.

Run (or let the watcher run) this file to rebuild the full assembly.
Parts are loaded fresh each time so edits to parts/*.py are picked up.
"""

import importlib.util
import os
import FreeCAD as App
import Part

# ── Helpers ──────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))


def load_part(rel_path):
    """Execute a part file as a fresh module and return its build() shape."""
    path = os.path.join(BASE, rel_path)
    spec = importlib.util.spec_from_file_location("_part", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.build()


def place(shape, x=0, y=0, z=0, yaw=0):
    """Return a copy of shape translated and optionally yaw-rotated (deg)."""
    s = shape.copy()
    s.Placement = App.Placement(
        App.Vector(x, y, z),
        App.Rotation(App.Vector(0, 0, 1), yaw),
    )
    return s


# ── Document ─────────────────────────────────────────────────────────

doc = App.activeDocument()
if doc is None:
    doc = App.newDocument("Assembly")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

# ── Build parts ───────────────────────────────────────────────────────

nema17 = load_part("parts/nema17.py")
byj48  = load_part("parts/byj48.py")

# ── Arrange ───────────────────────────────────────────────────────────
#
#   Place the NEMA 17 at the origin and the 28BYJ-48 60 mm to the right.
#   Both motors face the same direction (+Z shaft out).

parts = [
    ("NEMA17",  place(nema17,  x=  0)),
    ("28BYJ48", place(byj48,   x= 60)),
]

# ── Add to document ───────────────────────────────────────────────────

colors = {
    "NEMA17":  (0.65, 0.65, 0.70),   # brushed aluminium
    "28BYJ48": (0.20, 0.20, 0.20),   # dark plastic
}

for name, shape in parts:
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if App.GuiUp:
        obj.ViewObject.ShapeColor = colors.get(name, (0.8, 0.8, 0.8))

doc.recompute()

if App.GuiUp:
    import FreeCADGui as Gui
    Gui.SendMsgToActiveView("ViewFit")
