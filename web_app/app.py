from __future__ import annotations

import os
import random
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

import html
import re
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from markupsafe import Markup

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------

WEB_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = WEB_ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from logic.circuit_solver import CircuitSolver
from logic.problem_bank import ProblemBank
from logic.learning_modules import (
    create_kcl_module,
    create_kvl_module,
    create_mesh_module,
    create_nodal_module,
)

app = Flask(__name__)
app.secret_key = os.environ.get(
    "CIRCUIT_TUTOR_SECRET",
    "change-this-secret-before-public-deployment",
)

problem_bank = ProblemBank()
solver = CircuitSolver()

# ---------------------------------------------------------------------------
# Persistent data
# ---------------------------------------------------------------------------

if os.name == "nt":
    base_data = Path(
        os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
    )
else:
    base_data = Path.home() / ".local" / "share"

DATA_DIR = base_data / "CircuitAnalysisTutorWeb"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_FILE = DATA_DIR / "leaderboard.db"

LECTURER_PIN = os.environ.get("CIRCUIT_TUTOR_LECTURER_PIN", "1234")


def get_db() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade TEXT NOT NULL,
                score INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage REAL NOT NULL,
                time_seconds REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


init_db()

# ---------------------------------------------------------------------------
# Learning content
# ---------------------------------------------------------------------------

TOPIC_FACTORIES = {
    "kvl": create_kvl_module,
    "kcl": create_kcl_module,
    "mesh": create_mesh_module,
    "nodal": create_nodal_module,
}

TOPIC_META = {
    "kvl": {
        "title": "Kirchhoff's Voltage Law",
        "short": "KVL",
        "description": "Closed-loop voltage equations, sign conventions and voltage division.",
        "accent": "#e74c3c",
        "slide": None,
    },
    "kcl": {
        "title": "Kirchhoff's Current Law",
        "short": "KCL",
        "description": "Node-current equations, current division and parallel branches.",
        "accent": "#27ae60",
        "slide": None,
    },
    "mesh": {
        "title": "Mesh Analysis",
        "short": "Mesh",
        "description": "Systematic loop-current analysis for multi-loop circuits.",
        "accent": "#8e44ad",
        "slide": "Chapter 4 azral - Mesh Analysis.pdf",
    },
    "nodal": {
        "title": "Nodal Analysis",
        "short": "Nodal",
        "description": "Reference nodes, node-voltage equations and supernodes.",
        "accent": "#2980b9",
        "slide": "Chapter 3 azral - Nodal Analysis.pdf",
    },
}


TOPIC_FORMULAS = {
    "kvl": [
        {
            "label": "Loop law",
            "formula": "ΣV = 0",
            "meaning": "Every voltage rise is balanced by the voltage drops in one closed loop.",
        },
        {
            "label": "Series-loop current",
            "formula": "I = Vₛ / (R₁ + R₂ + ⋯ + Rₙ)",
            "meaning": "Use KVL with Ohm's law to calculate the same current through every series element.",
        },
        {
            "label": "Voltage divider",
            "formula": "Vᵣₖ = Vₛ · Rₖ / ΣR",
            "meaning": "A larger series resistance receives a larger share of the source voltage.",
        },
    ],
    "kcl": [
        {
            "label": "Node law",
            "formula": "ΣI = 0",
            "meaning": "The algebraic sum of all currents connected to a node is zero.",
        },
        {
            "label": "Current balance",
            "formula": "ΣIᵢₙ = ΣIₒᵤₜ",
            "meaning": "Current cannot accumulate at an ideal circuit node.",
        },
        {
            "label": "Parallel branch",
            "formula": "Iₖ = V / Rₖ",
            "meaning": "All parallel branches share the same voltage but can carry different currents.",
        },
    ],
    "mesh": [
        {
            "label": "Single-mesh drop",
            "formula": "Vᵣ = RI",
            "meaning": "A resistor belonging to one mesh carries that mesh current.",
        },
        {
            "label": "Shared resistor",
            "formula": "Vshared = R(I₁ − I₂)",
            "meaning": "Adjacent clockwise mesh currents oppose one another in their shared branch.",
        },
        {
            "label": "Two-mesh system",
            "formula": "(R₁+R₃)I₁ − R₃I₂ = Vₛ₁",
            "meaning": "Write one KVL equation per independent mesh and solve the equations together.",
        },
    ],
    "nodal": [
        {
            "label": "Branch current",
            "formula": "I = (Vnode − Vother) / R",
            "meaning": "Express every resistor current using the voltage difference across it.",
        },
        {
            "label": "Node equation",
            "formula": "Σ[(Vnode − Vk) / Rk] = Iinjected",
            "meaning": "Apply KCL after writing every connected branch current in voltage form.",
        },
        {
            "label": "Conductance form",
            "formula": "GV = I",
            "meaning": "Nodal equations can be organised into a compact conductance matrix.",
        },
    ],
}


LECTURE_NOTES = {
    "kvl": [
        {
            "tag": "01 · SEE THE LOOP",
            "title": "Read the loop as one continuous journey",
            "body": (
                "Choose a clockwise or anticlockwise traversal before writing "
                "anything. As you move through a source from − to +, record a "
                "voltage rise. Across a resistor in the current direction, "
                "record a voltage drop. Do not change the sign rule halfway."
            ),
            "formula": "−Vₛ + IR₁ + IR₂ + ⋯ = 0",
            "takeaway": (
                "A negative calculated current is not a failure—it simply "
                "means the real current flows opposite to your assumed arrow."
            ),
        },
        {
            "tag": "02 · BUILD THE EQUATION",
            "title": "Convert the circuit drawing into one clean equation",
            "body": (
                "Replace each resistor voltage by IR. In a series loop the "
                "same current appears in every resistor term, so it can be "
                "factored out. This turns a long KVL statement into one simple "
                "current calculation."
            ),
            "formula": "Vₛ = I(R₁ + R₂ + ⋯ + Rₙ)",
            "takeaway": (
                "Before using a calculator, estimate whether the current "
                "should increase or decrease when another resistor is added."
            ),
        },
        {
            "tag": "03 · PREDICT THE ANSWER",
            "title": "Use resistance size to predict voltage division",
            "body": (
                "Series resistors carry identical current. Therefore, the "
                "largest resistance must have the largest voltage drop. This "
                "quick prediction helps detect sign errors and incorrect "
                "calculator entries before you submit an answer."
            ),
            "formula": "V₁ : V₂ : V₃ = R₁ : R₂ : R₃",
            "takeaway": (
                "Your final resistor drops must add back to the source voltage."
            ),
        },
    ],
    "kcl": [
        {
            "tag": "01 · FOCUS ON ONE NODE",
            "title": "Treat a node as a current checkpoint",
            "body": (
                "Mark every branch connected to the selected node and assign "
                "an arrow to each branch current. Choose either currents "
                "entering as positive or currents leaving as positive, then "
                "keep that convention for the full equation."
            ),
            "formula": "I₁ + I₂ − I₃ − I₄ = 0",
            "takeaway": (
                "A negative branch current means the actual direction is "
                "opposite to the arrow you initially assumed."
            ),
        },
        {
            "tag": "02 · USE THE SHARED VOLTAGE",
            "title": "Turn parallel branches into simple Ohm's-law terms",
            "body": (
                "Every branch connected across the same two nodes has the same "
                "voltage. Calculate each branch current independently using "
                "I = V/R, then combine the currents using KCL."
            ),
            "formula": "Iₜ = V/R₁ + V/R₂ + ⋯",
            "takeaway": (
                "The smallest parallel resistance normally carries the largest "
                "branch current."
            ),
        },
        {
            "tag": "03 · CHECK CONSERVATION",
            "title": "Make the node balance before accepting the result",
            "body": (
                "Add all currents entering the node and compare them with the "
                "sum leaving. A mismatch indicates an arithmetic error, an "
                "incorrect direction sign, or a missing branch."
            ),
            "formula": "ΣIᵢₙ − ΣIₒᵤₜ = 0",
            "takeaway": (
                "KCL is a conservation law: charge does not disappear at a node."
            ),
        },
    ],
    "mesh": [
        {
            "tag": "01 · ASSIGN CURRENTS",
            "title": "Give every independent window one mesh current",
            "body": (
                "Clockwise arrows are normally chosen for convenience. The "
                "arrow is an assumption, not a guaranteed physical direction. "
                "A negative solution later reverses that assumed direction."
            ),
            "formula": "Mesh 1 → I₁     Mesh 2 → I₂",
            "takeaway": (
                "Use one mesh current per window, not one current per component."
            ),
        },
        {
            "tag": "02 · HANDLE THE SHARED BRANCH",
            "title": "Subtract opposing mesh currents in a shared resistor",
            "body": (
                "When two clockwise mesh currents pass through the same "
                "resistor in opposite directions, the branch current is their "
                "difference. The order of subtraction depends on which mesh "
                "equation you are writing."
            ),
            "formula": "Mesh 1 drop: R₃(I₁ − I₂)",
            "takeaway": (
                "In the Mesh 2 equation the same branch becomes R₃(I₂ − I₁)."
            ),
        },
        {
            "tag": "03 · FORM A SYSTEM",
            "title": "Solve the equations as one connected problem",
            "body": (
                "The diagonal coefficient contains all resistance around that "
                "mesh. The off-diagonal coefficient is the negative shared "
                "resistance. Once organised, simultaneous-equation solving "
                "becomes systematic."
            ),
            "formula": "[R] [I] = [V]",
            "takeaway": (
                "Check the final branch current in a shared resistor using I₁ − I₂."
            ),
        },
    ],
    "nodal": [
        {
            "tag": "01 · CHOOSE GROUND",
            "title": "Create a zero-volt reference before writing equations",
            "body": (
                "Select the most connected or convenient node as ground. Every "
                "other node voltage is measured relative to that reference. "
                "Good ground selection often reduces the number of unknowns."
            ),
            "formula": "Vground = 0 V",
            "takeaway": (
                "Node voltage is always a voltage between that node and ground."
            ),
        },
        {
            "tag": "02 · EXPRESS CURRENTS IN VOLTAGES",
            "title": "Write each branch current from the node outward",
            "body": (
                "For a resistor from V₁ to V₂, the current leaving V₁ is "
                "(V₁−V₂)/R. Repeat this pattern for every resistor touching the "
                "node, then include independent current sources with the chosen sign."
            ),
            "formula": "(V₁−V₂)/R + V₁/Rg = Is",
            "takeaway": (
                "Write the voltage at the node of interest first in every numerator."
            ),
        },
        {
            "tag": "03 · VERIFY THE NODE",
            "title": "Use current balance as the final accuracy check",
            "body": (
                "After calculating the node voltage, evaluate every branch "
                "current numerically. The total leaving current should equal "
                "the total entering current within rounding tolerance."
            ),
            "formula": "ΣIleaving = ΣIentering",
            "takeaway": (
                "A voltage outside the source range can still be valid when "
                "current sources are present."
            ),
        },
    ],
}


TOPIC_STUDY_TIPS = {
    "kvl": [
        {"label": "Fast check", "text": "Do all resistor drops add back to Vₛ?"},
        {"label": "Common mistake", "text": "Changing polarity signs halfway around the loop."},
        {"label": "Exam habit", "text": "Write the symbolic KVL equation before substituting numbers."},
    ],
    "kcl": [
        {"label": "Fast check", "text": "Does total current entering equal total current leaving?"},
        {"label": "Common mistake", "text": "Using different current sign conventions in one node equation."},
        {"label": "Exam habit", "text": "Label every branch arrow before applying Ohm's law."},
    ],
    "mesh": [
        {"label": "Fast check", "text": "Does each diagonal term contain every resistance in that mesh?"},
        {"label": "Common mistake", "text": "Adding shared currents instead of subtracting them."},
        {"label": "Exam habit", "text": "Keep all mesh arrows clockwise unless a source fixes a direction."},
    ],
    "nodal": [
        {"label": "Fast check", "text": "Do calculated branch currents satisfy KCL numerically?"},
        {"label": "Common mistake", "text": "Writing Vother − Vnode when currents leaving are positive."},
        {"label": "Exam habit", "text": "Choose ground first and clearly label every unknown node voltage."},
    ],
}


@app.template_filter("markdown")
def render_markdown(value: str) -> Markup:
    """Render the trusted lesson notes without an extra dependency."""
    def inline_format(line: str) -> str:
        escaped = html.escape(line)
        escaped = re.sub(
            r"\*\*(.+?)\*\*",
            r"<strong>\1</strong>",
            escaped,
        )
        escaped = re.sub(
            r"`(.+?)`",
            r"<code>\1</code>",
            escaped,
        )
        return escaped

    output: list[str] = []
    in_list = False

    for raw_line in (value or "").splitlines():
        line = raw_line.strip()

        if not line:
            if in_list:
                output.append("</ul>")
                in_list = False
            continue

        if line.startswith("### "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h3>{inline_format(line[4:])}</h3>")
            continue

        if line.startswith("## "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h2>{inline_format(line[3:])}</h2>")
            continue

        if line.startswith("# "):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<h1>{inline_format(line[2:])}</h1>")
            continue

        if line.startswith(">"):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(
                "<blockquote>"
                + inline_format(line.lstrip("> ").strip())
                + "</blockquote>"
            )
            continue

        if line.startswith(("* ", "- ")):
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{inline_format(line[2:])}</li>")
            continue

        numbered = re.match(r"^\d+\.\s+(.+)$", line)
        if numbered:
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{inline_format(numbered.group(1))}</li>")
            continue

        if in_list:
            output.append("</ul>")
            in_list = False

        output.append(f"<p>{inline_format(line)}</p>")

    if in_list:
        output.append("</ul>")

    return Markup("\n".join(output))


def module_for(topic: str):
    factory = TOPIC_FACTORIES.get(topic)
    if factory is None:
        abort(404)
    return factory()


# ---------------------------------------------------------------------------
# Resource discovery
# ---------------------------------------------------------------------------

def asset_roots() -> list[Path]:
    return [
        PROJECT_ROOT / "assets",
        PROJECT_ROOT / "assests",
    ]


def find_resource(kind: str, filename: str) -> Path | None:
    safe_name = Path(filename).name

    candidates: list[Path] = []

    if kind == "exam":
        for root_path in asset_roots():
            candidates.append(root_path / "exams" / safe_name)
        candidates.append(WEB_ROOT / "resources" / "exams" / safe_name)

    elif kind == "slide":
        for root_path in asset_roots():
            candidates.append(root_path / "learning" / "slides" / safe_name)
        candidates.append(WEB_ROOT / "resources" / "slides" / safe_name)

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    # Also support lecture/exam files stored directly or in nested folders.
    recursive_roots: list[Path] = []
    if kind == "exam":
        recursive_roots = [
            *(root / "exams" for root in asset_roots()),
            WEB_ROOT / "resources" / "exams",
        ]
    elif kind == "slide":
        recursive_roots = [
            *(root / "learning" for root in asset_roots()),
            WEB_ROOT / "resources" / "slides",
        ]

    for root in recursive_roots:
        if not root.exists():
            continue
        for match in root.rglob(safe_name):
            if match.is_file():
                return match

    return None



def find_topic_slide(topic: str) -> str | None:
    """Find an uploaded lecture PDF for a topic, including user asset folders."""
    preferred = TOPIC_META.get(topic, {}).get("slide")
    if preferred and find_resource("slide", preferred):
        return preferred

    keywords = {
        "kvl": ("kvl", "kirchhoff voltage"),
        "kcl": ("kcl", "kirchhoff current"),
        "mesh": ("mesh",),
        "nodal": ("nodal", "node voltage"),
    }.get(topic, ())

    search_roots = [
        *(root / "learning" / "slides" for root in asset_roots()),
        *(root / "learning" for root in asset_roots()),
        WEB_ROOT / "resources" / "slides",
    ]

    for root in search_roots:
        if not root.exists():
            continue
        for pdf in root.rglob("*.pdf"):
            lowered = pdf.name.lower()
            if any(keyword in lowered for keyword in keywords):
                return pdf.name

    return None


@app.route("/resource/<kind>/<path:filename>")
def resource_file(kind: str, filename: str):
    if kind not in {"exam", "slide"}:
        abort(404)

    resource = find_resource(kind, filename)
    if resource is None:
        abort(404)

    return send_from_directory(resource.parent, resource.name)


# ---------------------------------------------------------------------------
# Problem generation and checking
# ---------------------------------------------------------------------------

def solve_two_by_two(
    a: float,
    b: float,
    c: float,
    d: float,
    e: float,
    f: float,
) -> tuple[float, float]:
    determinant = a * d - b * c
    if abs(determinant) < 1e-12:
        raise ValueError("The generated equations are singular.")

    x = (e * d - b * f) / determinant
    y = (a * f - e * c) / determinant
    return x, y


def generate_topic_problem(
    topic: str,
    difficulty: str = "easy",
) -> dict[str, Any]:
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "easy"

    settings = {
        "easy": {
            "count": 2,
            "sources": [6, 9, 12, 18, 24],
            "r_min": 2,
            "r_max": 10,
        },
        "medium": {
            "count": 3,
            "sources": [12, 18, 20, 24, 30, 36],
            "r_min": 3,
            "r_max": 18,
        },
        "hard": {
            "count": 4,
            "sources": [24, 30, 36, 42, 48, 60],
            "r_min": 5,
            "r_max": 30,
        },
    }[difficulty]

    if topic == "kvl":
        source = random.choice(settings["sources"])
        resistors = [
            random.randint(settings["r_min"], settings["r_max"])
            for _ in range(settings["count"])
        ]
        total_resistance = sum(resistors)
        current = source / total_resistance

        ask_voltage = random.choice([True, False])
        target_index = random.randrange(len(resistors))

        solutions = {
            "I_total": current,
            "R_total": total_resistance,
        }

        components = [{"type": "V", "name": "V1", "value": source}]
        for index, value in enumerate(resistors, start=1):
            name = f"R{index}"
            components.append({"type": "R", "name": name, "value": value})
            solutions[f"V_{name}"] = current * value
            solutions[f"I_{name}"] = current

        if ask_voltage:
            target = f"V_R{target_index + 1}"
            question = (
                f"Use KVL to determine the voltage drop across "
                f"R{target_index + 1}."
            )
            unit = "V"
            hint = (
                "Choose a clockwise traversal. Write −Vs + IR1 + IR2 + … = 0. "
                "First calculate I = Vs/ΣR, then calculate the requested "
                f"drop using V_R{target_index + 1} = I × R{target_index + 1}."
            )
        else:
            target = "I_total"
            question = "Use KVL to determine the clockwise loop current."
            unit = "A"
            hint = (
                "Traverse the complete loop clockwise. The source is a rise "
                "and each resistor produces a drop: −Vs + IΣR = 0. "
                "Rearrange to I = Vs/ΣR."
            )

        return {
            "id": random.randint(1000, 9999),
            "topic": topic,
            "difficulty": difficulty,
            "description": (
                f"A {source} V source supplies {len(resistors)} series "
                "resistors. Apply Kirchhoff's Voltage Law."
            ),
            "question": question,
            "target_variable": target,
            "unit": unit,
            "hint": hint,
            "circuit_def": {
                "topology": "series",
                "components": components,
                "precalculated_solutions": solutions,
            },
        }

    if topic == "kcl":
        source = random.choice(settings["sources"])
        resistor_values = [
            random.randint(settings["r_min"], settings["r_max"])
            for _ in range(settings["count"])
        ]

        components = [{"type": "V", "name": "V1", "value": source}]
        solutions: dict[str, float] = {"V_total": float(source)}
        total_current = 0.0

        for index, value in enumerate(resistor_values, start=1):
            name = f"R{index}"
            branch_current = source / value
            components.append({"type": "R", "name": name, "value": value})
            solutions[f"I_{name}"] = branch_current
            solutions[f"V_{name}"] = float(source)
            total_current += branch_current

        solutions["I_total"] = total_current
        solutions["R_total"] = source / total_current

        ask_total = random.choice([True, False])
        if ask_total:
            target = "I_total"
            question = "Apply KCL to determine the total source current."
            hint = (
                "All branches have the same voltage. Calculate every branch "
                "current with I = V/R, then apply KCL: I_total = I1 + I2 + …."
            )
        else:
            branch = random.randint(1, len(resistor_values))
            target = f"I_R{branch}"
            question = f"Determine the current through branch R{branch}."
            hint = (
                "The voltage across each parallel branch equals the source "
                f"voltage. Use I_R{branch} = V/R{branch}, then check the node "
                "equation using KCL."
            )

        return {
            "id": random.randint(1000, 9999),
            "topic": topic,
            "difficulty": difficulty,
            "description": (
                f"A {source} V source is connected to "
                f"{len(resistor_values)} parallel branches."
            ),
            "question": question,
            "target_variable": target,
            "unit": "A",
            "hint": hint,
            "circuit_def": {
                "topology": "parallel",
                "components": components,
                "precalculated_solutions": solutions,
            },
        }

    if topic == "mesh":
        mesh_ranges = {
            "easy": (2, 8, [6, 8, 10, 12]),
            "medium": (3, 14, [8, 10, 12, 15, 18, 20]),
            "hard": (5, 24, [12, 18, 20, 24, 30, 36]),
        }
        r_min, r_max, sources = mesh_ranges[difficulty]
        r1 = random.randint(r_min, r_max)
        r2 = random.randint(r_min, r_max)
        r3 = random.randint(r_min, r_max)
        vs1 = random.choice(sources)
        vs2 = random.choice(sources[:-1])

        i1, i2 = solve_two_by_two(
            r1 + r3,
            -r3,
            -r3,
            r2 + r3,
            vs1,
            vs2,
        )

        targets = ["I1", "I2"]
        if difficulty == "hard":
            targets.append("I_shared")
        target = random.choice(targets)

        question_map = {
            "I1": "Determine clockwise mesh current I1.",
            "I2": "Determine clockwise mesh current I2.",
            "I_shared": "Determine the shared-branch current I1 − I2.",
        }

        return {
            "id": random.randint(1000, 9999),
            "topic": topic,
            "difficulty": difficulty,
            "description": (
                "A two-loop circuit contains one shared resistor. "
                "Assign clockwise mesh currents I1 and I2."
            ),
            "question": question_map[target],
            "target_variable": target,
            "unit": "A",
            "hint": (
                "Write one clockwise KVL equation for each loop. The shared "
                "resistor uses R3(I1−I2) in Loop 1 and R3(I2−I1) in Loop 2. "
                f"Equations: ({r1}+{r3})I1 − {r3}I2 = {vs1}; "
                f"−{r3}I1 + ({r2}+{r3})I2 = {vs2}. Solve simultaneously."
            ),
            "circuit_def": {
                "topology": "mesh_two_loop",
                "components": [],
                "values": {
                    "R1": r1,
                    "R2": r2,
                    "R3": r3,
                    "Vs1": vs1,
                    "Vs2": vs2,
                },
                "precalculated_solutions": {
                    "I1": i1,
                    "I2": i2,
                    "I_shared": i1 - i2,
                },
            },
        }

    if topic == "nodal":
        if difficulty == "hard":
            vs = random.choice([12, 18, 24, 30])
            r1 = random.randint(4, 16)
            r2 = random.randint(4, 18)
            r3 = random.randint(3, 14)
            r4 = random.randint(4, 18)
            current_source = random.choice([1, 2, 3])

            v1, v2 = solve_two_by_two(
                (1 / r1) + (1 / r2) + (1 / r3),
                -(1 / r3),
                -(1 / r3),
                (1 / r3) + (1 / r4),
                vs / r1,
                current_source,
            )
            target = random.choice(["V1", "V2"])

            return {
                "id": random.randint(1000, 9999),
                "topic": topic,
                "difficulty": difficulty,
                "description": (
                    "A two-node network contains a coupling resistor and an "
                    "independent current source."
                ),
                "question": f"Use nodal analysis to determine {target}.",
                "target_variable": target,
                "unit": "V",
                "hint": (
                    "Write KCL at both non-reference nodes. At V1 use "
                    "(V1−Vs)/R1 + V1/R2 + (V1−V2)/R3 = 0. At V2 use "
                    "(V2−V1)/R3 + V2/R4 − Is = 0. Solve the two equations."
                ),
                "circuit_def": {
                    "topology": "nodal_two_node",
                    "components": [],
                    "values": {
                        "Vs": vs,
                        "R1": r1,
                        "R2": r2,
                        "R3": r3,
                        "R4": r4,
                        "Is": current_source,
                    },
                    "precalculated_solutions": {"V1": v1, "V2": v2},
                },
            }

        nodal_ranges = {
            "easy": (2, 10, [6, 9, 12, 15, 18], [1, 2]),
            "medium": (4, 18, [12, 18, 20, 24, 30], [1, 2, 3, 4]),
        }
        r_min, r_max, sources, currents = nodal_ranges[difficulty]
        vs = random.choice(sources)
        r1 = random.randint(r_min, r_max)
        r2 = random.randint(r_min, r_max)
        current_source = random.choice(currents)

        node_voltage = (
            (vs / r1) + current_source
        ) / ((1 / r1) + (1 / r2))

        return {
            "id": random.randint(1000, 9999),
            "topic": topic,
            "difficulty": difficulty,
            "description": (
                "Node V1 is connected to a known voltage through R1, "
                "to ground through R2, and receives an independent current."
            ),
            "question": "Use nodal analysis to determine node voltage V1.",
            "target_variable": "V1",
            "unit": "V",
            "hint": (
                "Take ground as reference and write KCL at V1: "
                "(V1−Vs)/R1 + V1/R2 − Is = 0. Substitute the labelled "
                "values and solve for V1."
            ),
            "circuit_def": {
                "topology": "nodal_one_node",
                "components": [],
                "values": {
                    "Vs": vs,
                    "R1": r1,
                    "R2": r2,
                    "Is": current_source,
                },
                "precalculated_solutions": {"V1": node_voltage},
            },
        }

    raise ValueError(f"Unsupported topic: {topic}")

def generate_competition_problem() -> dict[str, Any]:
    topic = random.choice(list(TOPIC_FACTORIES))
    difficulty = random.choice(["easy", "medium", "hard"])
    return generate_topic_problem(topic, difficulty)


def get_correct_answer(problem: dict[str, Any]) -> float:
    target = problem["target_variable"]
    circuit_def = problem.get("circuit_def", {})

    precalculated = circuit_def.get("precalculated_solutions", {})
    if target in precalculated:
        return float(precalculated[target])

    solution = solver.solve_circuit(circuit_def)
    if "error" in solution:
        raise ValueError(str(solution["error"]))

    answer = solution.get(target)
    if answer is None:
        raise ValueError(
            f"Target variable {target!r} was not found in the solution."
        )

    return float(answer)


def problem_pdf_info(problem: dict[str, Any]) -> tuple[str | None, int | None]:
    if problem.get("display_type") != "pdf_page":
        return None, None

    filename = Path(problem.get("pdf_path", "")).name
    page = int(problem.get("page_number", 0)) + 1
    return filename, page


def grade_from_percentage(percentage: float) -> str:
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    return "F"


def ordered_results():
    with get_db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM leaderboard
            ORDER BY
                CASE grade
                    WHEN 'A' THEN 0
                    WHEN 'B' THEN 1
                    WHEN 'C' THEN 2
                    WHEN 'D' THEN 3
                    ELSE 4
                END,
                score DESC,
                time_seconds ASC,
                created_at ASC
            """
        ).fetchall()


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Learning modules
# ---------------------------------------------------------------------------

@app.route("/learning")
def learning_index():
    return render_template(
        "learning_index.html",
        topics=TOPIC_META,
    )


@app.route("/learning/<topic>")
def learning_topic(topic: str):
    module = module_for(topic)
    meta = TOPIC_META[topic]

    try:
        lesson_index = int(request.args.get("lesson", "0"))
    except ValueError:
        lesson_index = 0

    lesson_index = max(0, min(lesson_index, len(module.lessons) - 1))
    lesson = module.lessons[lesson_index]

    slide_filename = find_topic_slide(topic)
    slide_available = slide_filename is not None

    return render_template(
        "learning_topic.html",
        topic=topic,
        meta=meta,
        module=module,
        lesson=lesson,
        lesson_index=lesson_index,
        lecture_notes=LECTURE_NOTES[topic],
        formula_cards=TOPIC_FORMULAS[topic],
        study_tips=TOPIC_STUDY_TIPS[topic],
        slide_available=slide_available,
        slide_filename=slide_filename,
    )


@app.route("/learning/<topic>/practice/start", methods=["POST"])
def start_practice(topic: str):
    if topic not in TOPIC_FACTORIES:
        abort(404)

    difficulty = request.form.get("difficulty", "easy")
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "easy"

    total = random.randint(5, 8)
    session["practice"] = {
        "topic": topic,
        "difficulty": difficulty,
        "total": total,
        "number": 1,
        "correct": 0,
        "problem": generate_topic_problem(topic, difficulty),
        "answered": False,
        "feedback": "",
        "feedback_type": "",
    }
    return redirect(url_for("practice", topic=topic))


@app.route("/learning/<topic>/practice", methods=["GET", "POST"])
def practice(topic: str):
    if topic not in TOPIC_FACTORIES:
        abort(404)

    state = session.get("practice")
    if not state or state.get("topic") != topic:
        return redirect(url_for("learning_topic", topic=topic))

    show_hint = False

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "hint":
            show_hint = True

        elif action == "check":
            if not state.get("answered"):
                raw_answer = request.form.get("answer", "").strip()
                try:
                    user_answer = float(raw_answer)
                    correct_answer = get_correct_answer(state["problem"])

                    if round(user_answer, 2) == round(correct_answer, 2):
                        state["correct"] += 1
                        state["feedback"] = (
                            f"Correct. Answer: {correct_answer:.2f} "
                            f"{state['problem'].get('unit', '')}"
                        )
                        state["feedback_type"] = "success"
                        state["answered"] = True
                    else:
                        state["feedback"] = (
                            f"Incorrect. Correct answer: {correct_answer:.2f} "
                            f"{state['problem'].get('unit', '')}"
                        )
                        state["feedback_type"] = "error"
                        state["answered"] = False

                except ValueError:
                    state["feedback"] = "Enter a valid numerical answer."
                    state["feedback_type"] = "error"
                except Exception as error:
                    state["feedback"] = f"Unable to check answer: {error}"
                    state["feedback_type"] = "error"

        elif action == "next":
            if not state.get("answered"):
                state["feedback"] = "Check your answer before moving on."
                state["feedback_type"] = "error"
            elif state["number"] >= state["total"]:
                result = {
                    "topic": topic,
                    "correct": state["correct"],
                    "total": state["total"],
                    "percentage": round(
                        state["correct"] / state["total"] * 100,
                        1,
                    ),
                }
                session.pop("practice", None)
                session["practice_result"] = result
                return redirect(url_for("practice_result", topic=topic))
            else:
                state["number"] += 1
                state["problem"] = generate_topic_problem(
                    topic, state.get("difficulty", "easy")
                )
                state["answered"] = False
                state["auto_advance"] = False
                state["feedback"] = ""
                state["feedback_type"] = ""

        session["practice"] = state
        session.modified = True

    return render_template(
        "practice.html",
        state=state,
        meta=TOPIC_META[topic],
        show_hint=show_hint,
    )


@app.route("/learning/<topic>/practice/result")
def practice_result(topic: str):
    result = session.get("practice_result")
    if not result or result.get("topic") != topic:
        return redirect(url_for("learning_topic", topic=topic))

    return render_template(
        "practice_result.html",
        result=result,
        meta=TOPIC_META[topic],
    )


# ---------------------------------------------------------------------------
# Tutor mode
# ---------------------------------------------------------------------------

@app.route("/tutor", methods=["GET", "POST"])
def tutor():
    feedback = ""
    feedback_type = ""
    show_hint = False

    if "tutor_problem" not in session:
        session["tutor_problem"] = problem_bank.generate_problem(
            difficulty=session.get("tutor_difficulty", "easy")
        )

    problem = session["tutor_problem"]

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "new":
            session["tutor_problem"] = problem_bank.generate_problem(
                difficulty=session.get("tutor_difficulty", "easy")
            )
            return redirect(url_for("tutor"))

        if action == "difficulty":
            difficulty = request.form.get("difficulty", "easy")
            if difficulty not in {"easy", "medium", "hard"}:
                difficulty = "easy"

            session["tutor_difficulty"] = difficulty
            session["tutor_problem"] = problem_bank.generate_problem(
                difficulty=difficulty
            )
            return redirect(url_for("tutor"))

        if action == "hint":
            show_hint = True

        if action == "check":
            raw_answer = request.form.get("answer", "").strip()

            try:
                user_answer = float(raw_answer)
                correct_answer = get_correct_answer(problem)

                if abs(user_answer - correct_answer) < 0.1:
                    feedback = (
                        f"Correct. Answer: {correct_answer:.2f} "
                        f"{problem.get('unit', '')}."
                    )
                    feedback_type = "success"
                else:
                    feedback = (
                        f"Incorrect. Correct answer: {correct_answer:.2f} "
                        f"{problem.get('unit', '')}."
                    )
                    feedback_type = "error"

            except ValueError:
                feedback = "Enter a valid numerical answer."
                feedback_type = "error"
            except Exception as error:
                feedback = f"Unable to check the answer: {error}"
                feedback_type = "error"

    exam_filename, exam_page = problem_pdf_info(problem)

    return render_template(
        "tutor.html",
        problem=problem,
        feedback=feedback,
        feedback_type=feedback_type,
        show_hint=show_hint,
        difficulty=session.get("tutor_difficulty", "easy"),
        exam_filename=exam_filename,
        exam_page=exam_page,
    )


# ---------------------------------------------------------------------------
# Competitive mode
# ---------------------------------------------------------------------------

@app.route("/competitive")
def competitive_role():
    return render_template("competitive_role.html")


@app.route("/competitive/student", methods=["GET", "POST"])
def competitive_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Enter the student's name.", "error")
            return render_template("competitive_student.html")

        total = 10
        now = time.time()
        session["competition"] = {
            "name": name,
            "total": total,
            "number": 1,
            "correct": 0,
            "score": 0,
            "started": now,
            "question_started": now,
            "problem": generate_competition_problem(),
            "answered": False,
            "feedback": "",
            "feedback_type": "",
            "auto_advance": False,
        }
        return redirect(url_for("competitive_question"))

    return render_template("competitive_student.html")


@app.route("/competitive/question", methods=["GET", "POST"])
def competitive_question():
    state = session.get("competition")
    if not state:
        return redirect(url_for("competitive_student"))

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "check" and not state.get("answered"):
            raw_answer = request.form.get("answer", "").strip()

            try:
                user_answer = float(raw_answer)
                correct_answer = get_correct_answer(state["problem"])
                elapsed = time.time() - state["question_started"]

                if abs(user_answer - correct_answer) < 0.1:
                    state["correct"] += 1
                    speed_bonus = max(0, 5 - int(elapsed / 4))
                    points = 10 + speed_bonus
                    state["score"] += points
                    state["feedback"] = f"Correct. +{points} points."
                    state["feedback_type"] = "success"
                else:
                    state["feedback"] = (
                        f"Incorrect. Correct answer: {correct_answer:.2f} "
                        f"{state['problem'].get('unit', '')}"
                    )
                    state["feedback_type"] = "error"

                state["answered"] = True
                state["auto_advance"] = True

            except ValueError:
                state["feedback"] = "Enter a valid numerical answer."
                state["feedback_type"] = "error"
            except Exception as error:
                state["feedback"] = f"Unable to check answer: {error}"
                state["feedback_type"] = "error"

        elif action == "next":
            if not state.get("answered"):
                state["feedback"] = "Submit an answer before continuing."
                state["feedback_type"] = "error"

            elif state["number"] >= state["total"]:
                total_time = round(time.time() - state["started"], 2)
                percentage = round(
                    state["correct"] / state["total"] * 100,
                    1,
                )
                grade = grade_from_percentage(percentage)

                with get_db() as connection:
                    cursor = connection.execute(
                        """
                        INSERT INTO leaderboard
                        (
                            name, grade, score, correct, total,
                            percentage, time_seconds
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            state["name"],
                            grade,
                            state["score"],
                            state["correct"],
                            state["total"],
                            percentage,
                            total_time,
                        ),
                    )
                    result_id = cursor.lastrowid

                result = {
                    "id": result_id,
                    "name": state["name"],
                    "grade": grade,
                    "score": state["score"],
                    "correct": state["correct"],
                    "total": state["total"],
                    "percentage": percentage,
                    "time_seconds": total_time,
                }

                session.pop("competition", None)
                session["last_competition_result"] = result
                return redirect(url_for("competitive_result"))

            else:
                state["number"] += 1
                state["problem"] = generate_competition_problem()
                state["question_started"] = time.time()
                state["answered"] = False
                state["auto_advance"] = False
                state["feedback"] = ""
                state["feedback_type"] = ""

        session["competition"] = state
        session.modified = True

    return render_template(
        "competitive_question.html",
        state=state,
        topic_meta=TOPIC_META.get(
            state["problem"].get("topic", ""),
            {"short": "Circuit"},
        ),
    )


@app.route("/competitive/result")
def competitive_result():
    result = session.get("last_competition_result")
    if not result:
        return redirect(url_for("competitive_student"))

    return render_template(
        "competitive_result.html",
        result=result,
    )


@app.route("/competitive/leaderboard")
def leaderboard():
    return render_template(
        "leaderboard.html",
        results=ordered_results(),
    )


@app.route("/competitive/lecturer", methods=["GET", "POST"])
def lecturer_login():
    if request.method == "POST":
        pin = request.form.get("pin", "")
        if pin == LECTURER_PIN:
            session["is_lecturer"] = True
            return redirect(url_for("lecturer_dashboard"))

        flash("Incorrect lecturer PIN.", "error")

    return render_template("lecturer_login.html")


def lecturer_required() -> None:
    if not session.get("is_lecturer"):
        abort(403)


@app.route("/competitive/lecturer/dashboard")
def lecturer_dashboard():
    lecturer_required()
    return render_template(
        "lecturer_dashboard.html",
        results=ordered_results(),
    )


@app.route(
    "/competitive/lecturer/edit/<int:result_id>",
    methods=["GET", "POST"],
)
def lecturer_edit(result_id: int):
    lecturer_required()

    with get_db() as connection:
        result = connection.execute(
            "SELECT * FROM leaderboard WHERE id = ?",
            (result_id,),
        ).fetchone()

    if result is None:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        try:
            total = max(1, int(request.form.get("total", result["total"])))
            correct = int(request.form.get("correct", result["correct"]))
            correct = max(0, min(correct, total))
            score = max(0, int(request.form.get("score", result["score"])))
            time_seconds = max(
                0.0,
                float(
                    request.form.get(
                        "time_seconds",
                        result["time_seconds"],
                    )
                ),
            )
        except ValueError:
            flash("Use valid numerical values.", "error")
            return render_template(
                "lecturer_edit.html",
                result=result,
            )

        if not name:
            flash("Student name cannot be empty.", "error")
            return render_template(
                "lecturer_edit.html",
                result=result,
            )

        percentage = round(correct / total * 100, 1)
        grade = grade_from_percentage(percentage)

        with get_db() as connection:
            connection.execute(
                """
                UPDATE leaderboard
                SET
                    name = ?,
                    grade = ?,
                    score = ?,
                    correct = ?,
                    total = ?,
                    percentage = ?,
                    time_seconds = ?
                WHERE id = ?
                """,
                (
                    name,
                    grade,
                    score,
                    correct,
                    total,
                    percentage,
                    time_seconds,
                    result_id,
                ),
            )

        flash("Student result updated.", "success")
        return redirect(url_for("lecturer_dashboard"))

    return render_template(
        "lecturer_edit.html",
        result=result,
    )


@app.route(
    "/competitive/lecturer/delete/<int:result_id>",
    methods=["POST"],
)
def lecturer_delete(result_id: int):
    lecturer_required()

    with get_db() as connection:
        connection.execute(
            "DELETE FROM leaderboard WHERE id = ?",
            (result_id,),
        )

    flash("Student result deleted.", "success")
    return redirect(url_for("lecturer_dashboard"))


@app.route("/competitive/lecturer/clear", methods=["POST"])
def lecturer_clear():
    lecturer_required()

    pin = request.form.get("pin", "")
    if pin != LECTURER_PIN:
        flash("Incorrect PIN. No results were deleted.", "error")
        return redirect(url_for("lecturer_dashboard"))

    with get_db() as connection:
        connection.execute("DELETE FROM leaderboard")

    flash("All leaderboard results were deleted.", "success")
    return redirect(url_for("lecturer_dashboard"))


@app.route("/competitive/lecturer/logout")
def lecturer_logout():
    session.pop("is_lecturer", None)
    return redirect(url_for("competitive_role"))


# ---------------------------------------------------------------------------
# Helper mode
# ---------------------------------------------------------------------------

@app.route("/helper", methods=["GET", "POST"])
def helper():
    result = None
    error = None

    if request.method == "POST":
        topology = request.form.get("topology", "series")
        raw_voltage = request.form.get("voltage", "").strip()
        raw_resistors = request.form.get("resistors", "").strip()

        try:
            voltage = float(raw_voltage)
            resistors = [
                float(item.strip())
                for item in raw_resistors.split(",")
                if item.strip()
            ]

            if topology not in {"series", "parallel"}:
                raise ValueError("Choose series or parallel.")
            if not resistors:
                raise ValueError("Enter at least one resistor.")
            if any(value <= 0 for value in resistors):
                raise ValueError("Every resistance must be greater than zero.")

            if topology == "series":
                total_resistance = sum(resistors)
                total_current = voltage / total_resistance
                branches = [
                    {
                        "name": f"R{index}",
                        "resistance": resistance,
                        "voltage": total_current * resistance,
                        "current": total_current,
                    }
                    for index, resistance in enumerate(
                        resistors,
                        start=1,
                    )
                ]
            else:
                conductance = sum(1 / value for value in resistors)
                total_resistance = 1 / conductance
                total_current = voltage / total_resistance
                branches = [
                    {
                        "name": f"R{index}",
                        "resistance": resistance,
                        "voltage": voltage,
                        "current": voltage / resistance,
                    }
                    for index, resistance in enumerate(
                        resistors,
                        start=1,
                    )
                ]

            result = {
                "topology": topology,
                "voltage": voltage,
                "resistors": resistors,
                "total_resistance": total_resistance,
                "total_current": total_current,
                "branches": branches,
            }

        except ValueError as exc:
            error = str(exc)

    return render_template(
        "helper.html",
        result=result,
        error=error,
    )


# ---------------------------------------------------------------------------
# Visual circuit builder
# ---------------------------------------------------------------------------

@app.route("/builder")
def builder():
    return render_template("builder.html")


# ---------------------------------------------------------------------------
# Error pages
# ---------------------------------------------------------------------------

@app.errorhandler(403)
def forbidden(_error):
    return render_template(
        "message.html",
        title="Access Denied",
        message="Lecturer login is required to open this page.",
        return_url=url_for("lecturer_login"),
        return_label="Lecturer Login",
    ), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template(
        "message.html",
        title="Page Not Found",
        message="The requested page or resource could not be found.",
        return_url=url_for("index"),
        return_label="Return Home",
    ), 404


if __name__ == "__main__":
    print("Persistent leaderboard database:", DATABASE_FILE)
    app.run(debug=True)
