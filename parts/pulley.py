"""
60-tooth GT2 toothed belt pulley for 6 mm belt.

Spec (from 60t-pulley.jpg, corrected dimensions):
  Flange OD:     44 mm (two thin flanges, one each side of belt)
  Flange height: 1 mm each
  Belt section:  7 mm wide (accommodates 6 mm belt)
  Hub OD:        25 mm, 7 mm thick — top side only
  Bore:          6.35 mm (1/4 in)
  Teeth:         60 × GT2 (2 mm pitch)
  Total height:  16 mm  (1 + 7 + 1 + 7)

Stack (Z=0 at bottom):
  0– 1  bottom flange  44 mm OD
  1– 8  belt/teeth      ~38 mm OD
  8– 9  top flange     44 mm OD
  9–16  hub            25 mm OD

Tooth geometry (GT2 standard):
  Pitch:         2 mm
  Tooth depth:   0.75 mm
  Tooth width:   ~1.0 mm (simplified rectangular)
"""

import math
import FreeCAD as App
import Part

# ── Dimensions ────────────────────────────────────────────────────────────────

TEETH        = 60
PITCH        = 2.0       # GT2, mm
TOOTH_DEPTH  = 0.75      # mm
TOOTH_WIDTH  = 1.0       # mm (simplified rectangular)

FLANGE_OD    = 44.0      # mm
FLANGE_H     = 1.0       # mm
BELT_W       = 7.0       # mm (channel width; belt is 6 mm)
HUB_OD       = 25.0      # mm
HUB_H        = 7.0       # mm
BORE         = 6.35      # mm (1/4 in)

# Z positions
Z_BOT_FLANGE = 0.0
Z_BELT       = FLANGE_H                        # 1
Z_TOP_FLANGE = FLANGE_H + BELT_W              # 8
Z_HUB        = Z_TOP_FLANGE + FLANGE_H        # 9
TOTAL_H      = Z_HUB + HUB_H                  # 16

# Derived tooth geometry
PITCH_DIA    = (TEETH * PITCH) / math.pi      # ≈ 38.197 mm
ROOT_R       = PITCH_DIA / 2 - TOOTH_DEPTH    # root radius


def _tooth(z_base, height):
    """One rectangular tooth protruding radially outward from ROOT_R."""
    half_w = TOOTH_WIDTH / 2
    return Part.makeBox(
        TOOTH_DEPTH,
        TOOTH_WIDTH,
        height,
        App.Vector(ROOT_R, -half_w, z_base),
    )


def build():
    # ── Hub (top section only) ────────────────────────────────────────────────
    hub = Part.makeCylinder(HUB_OD / 2, HUB_H, App.Vector(0, 0, Z_HUB))

    # ── Flanges ───────────────────────────────────────────────────────────────
    flange_bot = Part.makeCylinder(FLANGE_OD / 2, FLANGE_H,
                                   App.Vector(0, 0, Z_BOT_FLANGE))
    flange_top = Part.makeCylinder(FLANGE_OD / 2, FLANGE_H,
                                   App.Vector(0, 0, Z_TOP_FLANGE))

    # ── Belt root cylinder ────────────────────────────────────────────────────
    root_cyl = Part.makeCylinder(ROOT_R, BELT_W, App.Vector(0, 0, Z_BELT))

    # ── Teeth (60 rectangular protrusions, polar array) ───────────────────────
    angle_step = 360.0 / TEETH
    base_tooth = _tooth(Z_BELT, BELT_W)
    teeth_shapes = []
    for i in range(TEETH):
        rot = App.Matrix()
        rot.rotateZ(math.radians(i * angle_step))
        teeth_shapes.append(base_tooth.transformGeometry(rot))

    teeth = teeth_shapes[0]
    for t in teeth_shapes[1:]:
        teeth = teeth.fuse(t)

    # ── Assemble + bore ───────────────────────────────────────────────────────
    body = hub.fuse(flange_bot).fuse(flange_top).fuse(root_cyl).fuse(teeth)
    bore = Part.makeCylinder(BORE / 2, TOTAL_H)
    return body.cut(bore)
