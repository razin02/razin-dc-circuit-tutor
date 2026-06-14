# DC Circuit Analysis Tutor — Web System V2

This version fixes the web issues reported during testing.

## V2 improvements

- Learning-module resistors use zig-zag schematic symbols.
- KVL and Mesh arrows show a complete clockwise loop direction.
- Mesh-current labels are separated from resistors and sources.
- Learning Modules show structured lecture notes and textbook support.
- Uploaded Mesh and Nodal lecture PDFs are embedded in the module page.
- KVL and KCL lecture PDFs are detected automatically when placed in the project learning assets.
- Learning practice includes Easy, Medium and Hard difficulty selection.
- Hard Nodal practice includes a two-node simultaneous-equation problem.
- Competitive Mode automatically advances after displaying answer feedback.
- Visual Builder now uses a real drag-and-drop SVG workspace.
- Builder components can be moved, rotated, edited and connected by terminals.
- Series and parallel auto-wiring are included as optional shortcuts.
- Designs can still be saved and loaded in the browser.

## Replace the old web version

1. Stop Flask with `Ctrl+C`.
2. Replace the old `web_app` folder with this folder.
3. From the main project folder, run:

```powershell
python -m pip install -r web_app\requirements.txt
python web_app\app.py
```

4. Open:

```text
http://127.0.0.1:5000
```

## Lecturer PIN

Default demonstration PIN:

```text
1234
```

## Persistent leaderboard

The web leaderboard remains stored in:

```text
%LOCALAPPDATA%\CircuitAnalysisTutorWeb\leaderboard.db
```

Replacing the `web_app` folder does not delete the leaderboard.
