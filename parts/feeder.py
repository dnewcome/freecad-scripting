import FreeCAD as App
import Part


def build():
    """Return a Part.Shape for a 1KGSSJ-B wire feeder drive unit (arm closed/locked).

    Orientation:
      Wire feed axis: +X  (inlet at X=0, outlet in +X direction).
      Front face (drive-roller / operator side): Y=0, body extends to Y=-body_d.
      Bottom of housing: Z=0.

    All dimensions taken exclusively from the 1KGSSJ-B manufacturer line drawing:

      Front view:
        body_l  = 104.5 mm  (base width, X)
        body_h  =  85.0 mm  (total height, Z)
        wire_z  =  47.3 mm  (wire-axis / roller-centre from bottom)
        nose_l  =  17.5 mm  (nose extends right: 122 - 104.5)
        nose_h  =  27.3 mm  (nose section height, centred on wire_z)
        nose_hole_d = 5.3 mm  (Ø5.3 outlet hole in nose)

      Side view:
        body_d       =  53.0 mm  (front-face to back-face of housing)
        motor_protr  =  40.0 mm  (motor protrudes from back: 93 - 53)
        → total depth = 93 mm

      Spec table:
        roller_od = 25.0 mm, roller_id = 7.0 mm, roller_h = 7.5 mm
    """
    # ── Parameters (mm) ─────────────────────────────────────────────
    body_l      = 104.5   # X – housing length
    body_d      =  53.0   # Y – housing depth (front face to back face)
    body_h      =  85.0   # Z – housing height
    fillet_r    =   3.0

    wire_z      =  47.3   # Z – wire / roller centreline

    # Nose (tapered protrusion at +X end of body)
    nose_l      =  17.5   # X – nose length  (122 - 104.5)
    nose_h      =  27.3   # Z – nose height (centred on wire_z)
    nose_d_tip  =  20.0   # Y – estimated nose tip depth (tapers from body_d)
    nose_hole_d =   5.3   # Ø outlet / fastener hole in nose face

    # Drive roller (spec table: Φ25×7×7.5 mm, on front face Y=0)
    roller_od   =  25.0
    roller_h    =   7.5
    roller_cx   =  body_l / 2   # X – placed at half the body length

    # Motor housing (back face protrusion, from side-view 93-53 = 40 mm)
    motor_protr =  40.0          # Y protrusion from back face
    motor_d     =  40.0          # Ø motor can (equals the protrusion depth)
    motor_cx    =  roller_cx     # X – aligned with roller
    motor_cz    =  wire_z        # Z – centred on wire axis

    # Inlet tube stub on left face (X=0)
    inlet_tube_od = 10.0
    inlet_tube_id =  4.0
    inlet_ext     = 15.0   # how far the stub extends in -X beyond body

    # Tension adjustment knob (top-left, upper surface of body)
    knob_od   = 28.0
    knob_h    = 25.0
    knob_cx   = 18.0          # X – near left edge
    knob_cy   = -body_d / 2   # Y – centred in body depth

    # Tensioning arm in closed/locked position – modelled as a flat plate
    # lying on the body top face.  The total 85 mm height is the body; the
    # closed arm sits flush with (or just above) the top face.
    arm_l      =  70.0   # X – arm length
    arm_d      =  body_d # Y – spans full body depth
    arm_thick  =   6.0   # Z – plate thickness (arm sits above body_h)
    arm_x0     =  15.0   # X – left edge of arm
    arm_fillet =   2.0

    # Mounting holes: Ø5.3 at body corners, through in Y direction
    hole_d  =   5.3
    hole_mx =   9.0   # X margin from edge
    hole_mz =   9.0   # Z margin from edge

    # ── Main body ────────────────────────────────────────────────────
    body_box = Part.makeBox(body_l, body_d, body_h,
                            App.Vector(0, -body_d, 0))
    z_edges = [e for e in body_box.Edges
               if abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) < 0.01
               and abs(e.Vertexes[0].Point.y - e.Vertexes[1].Point.y) < 0.01]
    try:
        body = body_box.makeFillet(fillet_r, z_edges)
    except Exception:
        body = body_box

    # ── Nose (tapered frustum on +X end) ─────────────────────────────
    # In the front view the nose spans nose_h in Z, centred on wire_z.
    # In the side view it tapers from body_d to nose_d_tip.
    z0   = wire_z - nose_h / 2
    z1   = wire_z + nose_h / 2
    bx   = body_l
    ex   = body_l + nose_l
    sy   = (body_d - nose_d_tip) / 2   # Y taper per side
    sz   = nose_h / 8                  # small Z taper at tip for realism

    w_base = Part.makePolygon([
        App.Vector(bx,  0,       z0),
        App.Vector(bx, -body_d,  z0),
        App.Vector(bx, -body_d,  z1),
        App.Vector(bx,  0,       z1),
        App.Vector(bx,  0,       z0),
    ])
    w_tip = Part.makePolygon([
        App.Vector(ex, -sy,              z0 + sz),
        App.Vector(ex, -(sy + nose_d_tip), z0 + sz),
        App.Vector(ex, -(sy + nose_d_tip), z1 - sz),
        App.Vector(ex, -sy,              z1 - sz),
        App.Vector(ex, -sy,              z0 + sz),
    ])
    try:
        nose_shape = Part.makeLoft([w_base, w_tip], True, False)
    except Exception:
        # Fallback: plain box approximation
        nose_shape = Part.makeBox(nose_l, nose_d_tip, nose_h,
                                  App.Vector(bx, -sy - nose_d_tip, z0))

    # Ø5.3 outlet / fastener hole through nose face (at wire axis height)
    nose_cy = -(body_d / 2)
    nose_hole = Part.makeCylinder(
        nose_hole_d / 2, nose_l + 1,
        App.Vector(body_l - 0.5, nose_cy, wire_z),
        App.Vector(1, 0, 0)
    )

    # ── Motor housing (protrudes from back face Y=-body_d in -Y) ─────
    motor = Part.makeCylinder(
        motor_d / 2, motor_protr,
        App.Vector(motor_cx, -body_d, motor_cz),
        App.Vector(0, -1, 0)
    )

    # ── Drive roller (protrudes from front face Y=0 in +Y) ───────────
    drive_roller = Part.makeCylinder(
        roller_od / 2, roller_h,
        App.Vector(roller_cx, 0, wire_z),
        App.Vector(0, 1, 0)
    )

    # Shallow recess in front face around roller
    recess = Part.makeCylinder(
        roller_od / 2 + 3, 4.0,
        App.Vector(roller_cx, 0.1, wire_z),
        App.Vector(0, -1, 0)
    )

    # ── Inlet tube stub (left face, X=0) ─────────────────────────────
    cy = -body_d / 2
    inlet_outer = Part.makeCylinder(
        inlet_tube_od / 2, inlet_ext,
        App.Vector(-inlet_ext, cy, wire_z),
        App.Vector(1, 0, 0)
    )
    inlet_bore = Part.makeCylinder(
        inlet_tube_id / 2, inlet_ext + body_d / 2 + 5,
        App.Vector(-inlet_ext, cy, wire_z),
        App.Vector(1, 0, 0)
    )
    inlet_tube = inlet_outer.cut(inlet_bore)

    # ── Tensioning arm plate (closed/locked, on body top) ────────────
    arm_box = Part.makeBox(arm_l, arm_d, arm_thick,
                           App.Vector(arm_x0, -arm_d, body_h))
    arm_z_edges = [e for e in arm_box.Edges
                   if abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) < 0.01
                   and abs(e.Vertexes[0].Point.y - e.Vertexes[1].Point.y) < 0.01]
    try:
        arm = arm_box.makeFillet(arm_fillet, arm_z_edges)
    except Exception:
        arm = arm_box

    # ── Tension adjustment knob ───────────────────────────────────────
    knob = Part.makeCylinder(
        knob_od / 2, knob_h,
        App.Vector(knob_cx, knob_cy, body_h + arm_thick),
        App.Vector(0, 0, 1)
    )

    # ── Mounting holes: Ø5.3 through body in Y ───────────────────────
    holes = []
    for hx in [hole_mx, body_l - hole_mx]:
        for hz in [hole_mz, body_h - hole_mz]:
            h = Part.makeCylinder(
                hole_d / 2, body_d + 2,
                App.Vector(hx, 1, hz),
                App.Vector(0, -1, 0)
            )
            holes.append(h)

    # ── Assemble ──────────────────────────────────────────────────────
    shape = body.fuse(nose_shape)
    shape = shape.fuse(motor)
    shape = shape.fuse(drive_roller)
    shape = shape.fuse(inlet_tube)
    shape = shape.fuse(arm)
    shape = shape.fuse(knob)
    shape = shape.cut(recess)
    shape = shape.cut(nose_hole)
    for h in holes:
        shape = shape.cut(h)

    return shape.removeSplitter()
