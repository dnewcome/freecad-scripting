import FreeCAD as App
import Part

doc = App.activeDocument()
if doc is None:
    doc = App.newDocument("StepperMotor")

for obj in doc.Objects:
    doc.removeObject(obj.Name)

# ── NEMA 17 parameters (mm) ──────────────────────────────────────────
body_w     = 42.0   # body width and depth
body_len   = 40.0   # body length (axis direction)
corner_r   = 2.5    # corner fillet radius

pilot_d    = 22.0   # pilot boss diameter
pilot_h    =  2.0   # pilot boss protrusion

shaft_d    =  5.0   # shaft diameter
shaft_len  = 24.0   # shaft protrusion beyond front face

hole_d     =  3.2   # M3 clearance diameter
hole_depth =  4.5   # blind hole depth
hole_pitch = 31.0   # hole center-to-center spacing

# Orientation: front face (shaft side) at Z=0, body extends to Z=-body_len,
# shaft and pilot boss extend to Z=+...

half = body_w / 2

# ── Body ─────────────────────────────────────────────────────────────
body_box = Part.makeBox(body_w, body_w, body_len,
                        App.Vector(-half, -half, -body_len))

# Fillet the 4 vertical (Z-axis) edges
z_edges = [e for e in body_box.Edges
           if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > body_len / 2]
try:
    body = body_box.makeFillet(corner_r, z_edges)
except Exception:
    body = body_box  # fallback: square corners

# ── Pilot boss ───────────────────────────────────────────────────────
pilot = Part.makeCylinder(pilot_d / 2, pilot_h,
                          App.Vector(0, 0, 0),
                          App.Vector(0, 0, 1))

# ── Shaft ─────────────────────────────────────────────────────────────
shaft = Part.makeCylinder(shaft_d / 2, shaft_len,
                          App.Vector(0, 0, 0),
                          App.Vector(0, 0, 1))

# D-flat on shaft: cut a slab offset from center
flat_offset = 2.0  # distance from shaft center to flat face
flat_cut = Part.makeBox(shaft_d, shaft_d, shaft_len,
                        App.Vector(-shaft_d / 2, flat_offset, 0))
shaft = shaft.cut(flat_cut)

# ── Mounting holes (blind, cut into front face) ───────────────────────
hp = hole_pitch / 2
hole_starts = [
    App.Vector( hp,  hp, 0),
    App.Vector(-hp,  hp, 0),
    App.Vector( hp, -hp, 0),
    App.Vector(-hp, -hp, 0),
]

holes = [
    Part.makeCylinder(hole_d / 2, hole_depth, pos, App.Vector(0, 0, -1))
    for pos in hole_starts
]

# ── Assemble ─────────────────────────────────────────────────────────
motor = body.fuse(pilot).fuse(shaft)
for h in holes:
    motor = motor.cut(h)

motor = motor.removeSplitter()  # clean up internal faces

# ── Add to document ───────────────────────────────────────────────────
feature = doc.addObject("Part::Feature", "NEMA17")
feature.Shape = motor
doc.recompute()

if App.GuiUp:
    import FreeCADGui as Gui
    feature.ViewObject.ShapeColor = (0.65, 0.65, 0.70)  # brushed aluminum
    feature.ViewObject.Transparency = 0
    Gui.SendMsgToActiveView("ViewFit")
