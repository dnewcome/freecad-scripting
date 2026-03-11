"""
20-tooth GT2 toothed belt pulley for 6 mm belt.

Spec (from 20t-pulley.jpg):
  Flange OD:       16 mm
  Belt section:    7.1 mm tall (includes two thin flanges)
  Hub OD:          16 mm (same as flange OD)
  Hub height:      7.4 mm — top side only, with M4 set screw
  Bore:            6.35 mm (1/4 in)
  Teeth:           20 × GT2 (2 mm pitch)
  Total height:    14.5 mm  (7.1 + 7.4)

Stack (Z=0 at bottom):
  0–7.1   belt/teeth section, flanges at 16 mm OD, teeth at ~12.73 mm pitch dia
  7.1–14.5  hub, 11 mm OD, M4 set screw

Tooth geometry (GT2 standard):
  Pitch:           2 mm
  Tooth depth:     0.75 mm
  Tooth width:     ~1.0 mm (simplified rectangular)
"""

import math
import FreeCAD as App
import Part

# ── Dimensions ────────────────────────────────────────────────────────────────

TEETH        = 20
PITCH        = 2.0       # GT2, mm
TOOTH_DEPTH  = 0.75      # mm
TOOTH_WIDTH  = 1.0       # mm (simplified rectangular)

FLANGE_OD    = 16.0      # mm
FLANGE_H     = 1.0       # mm (thin flanges each side of belt)
BELT_W       = 7.1 - 2 * FLANGE_H   # 5.1 mm channel between flanges
HUB_OD       = 16.0      # mm (same as flange OD)
HUB_H        = 7.4       # mm
BORE         = 6.35      # mm (1/4 in)
SETSCREW_D   = 4.0       # M4

# Z positions
Z_BOT_FLANGE = 0.0
Z_BELT       = FLANGE_H
Z_TOP_FLANGE = FLANGE_H + BELT_W
Z_HUB        = Z_BOT_FLANGE + 7.1
TOTAL_H      = Z_HUB + HUB_H        # 14.5 mm

# Derived tooth geometry
PITCH_DIA    = (TEETH * PITCH) / math.pi   # ≈ 12.732 mm
ROOT_R       = PITCH_DIA / 2 - TOOTH_DEPTH


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
    # ── Flanges ───────────────────────────────────────────────────────────────
    flange_bot = Part.makeCylinder(FLANGE_OD / 2, FLANGE_H,
                                   App.Vector(0, 0, Z_BOT_FLANGE))
    flange_top = Part.makeCylinder(FLANGE_OD / 2, FLANGE_H,
                                   App.Vector(0, 0, Z_TOP_FLANGE))

    # ── Belt root cylinder ────────────────────────────────────────────────────
    root_cyl = Part.makeCylinder(ROOT_R, BELT_W, App.Vector(0, 0, Z_BELT))

    # ── Teeth (20 rectangular protrusions, polar array) ───────────────────────
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

    # ── Hub (top section, with M4 set screw) ──────────────────────────────────
    hub = Part.makeCylinder(HUB_OD / 2, HUB_H, App.Vector(0, 0, Z_HUB))

    screw_h = HUB_OD        # cut all the way through
    setscrew = Part.makeCylinder(
        SETSCREW_D / 2, screw_h,
        App.Vector(-screw_h / 2, 0, Z_HUB + HUB_H / 2),
        App.Vector(1, 0, 0),   # radial direction
    )

    # ── Assemble + bore ───────────────────────────────────────────────────────
    body = flange_bot.fuse(flange_top).fuse(root_cyl).fuse(teeth).fuse(hub)
    bore = Part.makeCylinder(BORE / 2, TOTAL_H)
    body = body.cut(bore).cut(setscrew)

    return body
