# FreeCAD Scripting — Live Reload Workflow

A code-driven 3D modelling setup for FreeCAD. Models are written as plain Python
files and FreeCAD automatically rebuilds the scene every time a file is saved.

---

## Project Layout

```
freecad-scripting/
├── watcher_macro.py   FreeCAD macro — run once to enable live reload
├── assembly.py        Entry point — positions and combines all parts
└── parts/
    ├── nema17.py      NEMA 17 stepper motor model
    └── byj48.py       28BYJ-48 5 V stepper motor model
```

### `parts/`

Each file in `parts/` defines a single component. The only requirement is a
top-level `build()` function that returns a `Part.Shape`:

```python
# parts/my_part.py
import FreeCAD as App
import Part

def build():
    shape = Part.makeBox(10, 10, 10)
    # ... boolean ops, fillets, etc.
    return shape
```

Parts know nothing about the document or the assembly — they just build and
return geometry. This keeps them self-contained and easy to test in isolation.

### `assembly.py`

The assembly is the entry point that the watcher executes on every reload. It:

1. Clears the active FreeCAD document.
2. Loads each part file with `load_part()`, which executes the file as a fresh
   module and calls its `build()` function. Loading is always fresh — Python's
   module cache is bypassed — so edits to any part file are picked up
   automatically.
3. Positions each shape with `place()`.
4. Adds the resulting shapes to the FreeCAD document and triggers a recompute.

To add a new part to the assembly:

```python
# in assembly.py
my_part = load_part("parts/my_part.py")

parts = [
    ("NEMA17",   place(nema17,  x=  0)),
    ("28BYJ48",  place(byj48,   x= 60)),
    ("MyPart",   place(my_part, x=120)),   # ← add this line
]
```

#### `place(shape, x, y, z, yaw)`

A small helper that returns a translated and optionally yaw-rotated copy of a
shape without modifying the original. `yaw` is in degrees around the Z axis.

#### Part orientation convention

All parts are modelled with the **front face (shaft / output side) at Z = 0**,
the body extending in the **−Z** direction, and protrusions (shaft, boss) in
the **+Z** direction. This makes it straightforward to align parts in the
assembly using only X/Y translations and Z rotations in most cases.

---

## The Watcher

`watcher_macro.py` is a FreeCAD macro (not a standalone script). It hooks into
FreeCAD's Qt event loop using a `QTimer` so it can poll for file changes in the
background without blocking the UI.

### How it works

1. **Startup** — when the macro runs it records the modification time (`mtime`)
   of every `.py` file found recursively under the project directory, then
   immediately executes `assembly.py` so the scene appears straight away.

2. **Polling** — every 500 ms the timer fires `_check()`, which rescans all
   `.py` files and compares their current `mtime` against the stored snapshot.

3. **Reload** — if any file has changed, the new snapshot is saved and
   `assembly.py` is re-executed via `exec()`. The changed file names are printed
   to the FreeCAD Report View.

4. **Error handling** — if `assembly.py` (or any part it loads) raises an
   exception, the full traceback is printed to the Report View in red. FreeCAD
   itself is unaffected and the watcher keeps running.

5. **Re-run safety** — re-running the macro stops the previously running timer
   before starting a new one, so you never end up with multiple watchers
   competing.

### Why `exec()` instead of `import`?

Python's import system caches modules in `sys.modules`. Re-importing a changed
file would return the cached version. `assembly.py` side-steps this by using
`importlib.util.spec_from_file_location` to load each part into a **throwaway
module object**, guaranteeing a fresh execution every time regardless of the
cache.

---

## Setup

### Requirements

- FreeCAD 1.x (tested with the AppImage release)
- No external Python packages — only FreeCAD's bundled Python and PySide2

### First-time setup

**1. Open FreeCAD**

```
/opt/FreeCAD_1.0.2-conda-Linux-x86_64-py311.AppImage
```

**2. Open the Macro dialog**

`Macro` menu → `Macros…`

**3. Point FreeCAD at the project directory**

In the Macro dialog, click **User macros location** (or the folder icon) and
navigate to the `freecad-scripting/` directory. FreeCAD will then find
`watcher_macro.py` in the list.

**4. Execute the watcher**

Select `watcher_macro.py` in the list and click **Execute**. You should see in
the Report View:

```
[watcher] watching /path/to/freecad-scripting (entry: assembly.py, every 500ms)
[watcher] reloaded assembly.py
```

Both motor models will appear in the 3D view.

**5. Edit and save**

Open any file in `parts/` or `assembly.py` in your editor. Save the file.
Within 500 ms FreeCAD rebuilds the scene and prints:

```
[watcher] changed: parts/nema17.py
[watcher] reloaded assembly.py
```

### Re-running the watcher

If you restart FreeCAD or want to reset the watcher, simply run
`watcher_macro.py` again from the Macro dialog. The previous timer is stopped
automatically.

### Checking the Report View

`View` menu → `Panels` → `Report View` shows all `[watcher]` messages,
including errors. Keep it open while editing.

---

## Adding a New Part

1. Create `parts/my_widget.py` with a `build()` function that returns a
   `Part.Shape`.
2. In `assembly.py`, call `load_part("parts/my_widget.py")` and add the result
   to the `parts` list with a `place()` call.
3. Save either file — the watcher rebuilds immediately.

## Models

### NEMA 17 (`parts/nema17.py`)

Standard NEMA 17 frame stepper motor. All dimensions parametric at the top of
the file.

| Feature | Dimension |
|---|---|
| Body | 42 × 42 × 40 mm |
| Corner fillet | R 2.5 mm |
| Pilot boss | Ø 22 × 2 mm |
| Shaft | Ø 5 × 24 mm, D-flat |
| Mounting holes | 4× M3, 31 mm pattern |

### 28BYJ-48 (`parts/byj48.py`)

Small geared 5 V stepper motor. Dimensions from the Kiatronics datasheet.

| Feature | Dimension |
|---|---|
| Body | Ø 28 × 19 mm |
| Front boss | Ø 9 × 2 mm |
| Shaft | Ø 5 × 6 mm, D-flat |
| Mounting tabs | 35 mm span, Ø 4.2 mm holes, R 3.5 cap, 1.5 mm thick |
