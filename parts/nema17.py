import FreeCAD as App
import Part


def build():
    """Return a Part.Shape for a NEMA 17 stepper motor.

    Orientation: front face (shaft side) at Z=0, body extends to Z=-body_len,
    shaft and pilot boss protrude in +Z.
    """
    # ── Parameters (mm) ─────────────────────────────────────────────
    body_w     = 42.0   # body width and depth
    body_len   = 40.0   # body length
    corner_r   =  2.5   # corner fillet radius

    pilot_d    = 22.0   # pilot boss diameter
    pilot_h    =  2.0   # pilot boss protrusion

    shaft_d    =  5.0   # shaft diameter
    shaft_len  = 24.0   # shaft protrusion beyond front face
    flat_offset=  2.0   # D-flat: mm from shaft center to flat face

    hole_d     =  3.2   # M3 clearance hole diameter
    hole_depth =  4.5   # blind hole depth
    hole_pitch = 31.0   # hole center-to-center spacing

    half = body_w / 2

    # ── Body ────────────────────────────────────────────────────────
    box = Part.makeBox(body_w, body_w, body_len,
                       App.Vector(-half, -half, -body_len))
    z_edges = [e for e in box.Edges
               if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > body_len / 2]
    try:
        body = box.makeFillet(corner_r, z_edges)
    except Exception:
        body = box

    # ── Pilot boss ──────────────────────────────────────────────────
    pilot = Part.makeCylinder(pilot_d / 2, pilot_h)

    # ── Shaft with D-flat ───────────────────────────────────────────
    shaft = Part.makeCylinder(shaft_d / 2, shaft_len)
    flat_cut = Part.makeBox(shaft_d, shaft_d, shaft_len,
                            App.Vector(-shaft_d / 2, flat_offset, 0))
    shaft = shaft.cut(flat_cut)

    # ── Mounting holes ──────────────────────────────────────────────
    hp = hole_pitch / 2
    holes = [
        Part.makeCylinder(hole_d / 2, hole_depth,
                          App.Vector(x, y, 0), App.Vector(0, 0, -1))
        for x, y in [(hp, hp), (-hp, hp), (hp, -hp), (-hp, -hp)]
    ]

    # ── Assemble ────────────────────────────────────────────────────
    shape = body.fuse(pilot).fuse(shaft)
    for h in holes:
        shape = shape.cut(h)

    return shape.removeSplitter()
