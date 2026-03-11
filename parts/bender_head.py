"""
Bender head — imported from bender-head.scad via OpenSCAD.

OpenSCAD renders the file to a temp STL; FreeCAD imports it as a mesh
and converts to a Part solid so it matches the other parts' build() contract.
"""

import os
import subprocess
import tempfile

import FreeCAD as App
import Mesh
import Part

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD_FILE = os.path.join(BASE, "bender-head.scad")


def build():
    tmp = tempfile.mktemp(suffix=".stl")
    try:
        subprocess.run(
            ["openscad", "-o", tmp, SCAD_FILE],
            check=True,
            capture_output=True,
        )
        mesh = Mesh.Mesh(tmp)
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh.Topology, 0.1)
        return Part.makeSolid(shape)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
