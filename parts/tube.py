"""
Stainless steel tube.

  OD: 1/4 in (6.35 mm)
  ID: 5 mm
  Length: 100 mm
"""

import Part

OD     = 25.4 * 0.25   # 6.35 mm
ID     = 5.0            # mm
LENGTH = 100.0          # mm


def build():
    outer = Part.makeCylinder(OD / 2, LENGTH)
    inner = Part.makeCylinder(ID / 2, LENGTH)
    return outer.cut(inner)
