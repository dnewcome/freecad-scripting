import FreeCAD as App
import Part


def build():
    """Return a Part.Shape for a 28BYJ-48 5V stepper motor.

    Orientation: front face (shaft side) at Z=0, body extends to Z=-body_len,
    shaft and boss protrude in +Z.

    Key dimensions from datasheet drawing:
      body: Ø28 mm, 19 mm long
      front boss: Ø9 mm, ~2 mm protrusion
      shaft: Ø5 mm, 6 mm protrusion, with D-flat
      mounting tabs: two ears on ±X axis, hole centers at ±17.5 mm (35 mm span)
                     tab width 8 mm, end radius R3.5, hole Ø4.2 mm
                     tab plate is 1.5 mm thick, flush with front face
    """
    # ── Parameters (mm) ─────────────────────────────────────────────
    body_d      = 28.0
    body_len    = 19.0

    boss_d      =  9.0
    boss_h      =  2.0

    shaft_d     =  5.0
    shaft_len   =  6.0
    flat_offset =  2.0   # D-flat: mm from shaft center to flat face

    tab_span    = 35.0   # hole center-to-center (X axis)
    tab_hole_d  =  4.2
    tab_r       =  3.5   # rounded cap radius at hole end
    tab_w       =  8.0   # tab width (Y direction)
    tab_thick   =  1.5   # tab plate thickness

    # ── Body ────────────────────────────────────────────────────────
    body = Part.makeCylinder(body_d / 2, body_len,
                             App.Vector(0, 0, -body_len),
                             App.Vector(0, 0, 1))

    # ── Front boss ──────────────────────────────────────────────────
    boss = Part.makeCylinder(boss_d / 2, boss_h)

    # ── Shaft with D-flat ───────────────────────────────────────────
    shaft = Part.makeCylinder(shaft_d / 2, shaft_len)
    flat_cut = Part.makeBox(shaft_d, shaft_d, shaft_len,
                            App.Vector(-shaft_d / 2, flat_offset, 0))
    shaft = shaft.cut(flat_cut)

    # ── Mounting tabs ────────────────────────────────────────────────
    # Each tab: rectangular body + rounded cap at outer end, then hole cut.
    # Plate sits at Z = -tab_thick … 0 (flush with front face).
    hole_x = tab_span / 2        # 17.5
    hw     = tab_w / 2           #  4.0

    tabs = []
    for sign in (+1, -1):
        cx = sign * hole_x

        # Rectangular part from body edge outward (generous width)
        inner_x = sign * (body_d / 2 - 1)   # starts just inside body edge
        outer_x = cx + sign * tab_r          # extends past hole center by R

        x0 = min(inner_x, outer_x)
        x1 = max(inner_x, outer_x)
        tab_rect = Part.makeBox(x1 - x0, tab_w, tab_thick,
                                App.Vector(x0, -hw, -tab_thick))

        # Rounded cap centred on hole
        cap = Part.makeCylinder(tab_r, tab_thick,
                                App.Vector(cx, 0, -tab_thick),
                                App.Vector(0, 0, 1))
        tab_shape = tab_rect.fuse(cap)

        # Cut mounting hole through tab
        hole = Part.makeCylinder(tab_hole_d / 2, tab_thick + 2,
                                 App.Vector(cx, 0, -tab_thick - 1),
                                 App.Vector(0, 0, 1))
        tab_shape = tab_shape.cut(hole)
        tabs.append(tab_shape)

    # ── Assemble ────────────────────────────────────────────────────
    shape = body.fuse(boss).fuse(shaft)
    for tab in tabs:
        shape = shape.fuse(tab)

    # Trim tab rectangles to body boundary where they overlap
    # (avoids internal faces where tab merges with cylinder)
    return shape.removeSplitter()
