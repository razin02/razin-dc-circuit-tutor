# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_pdf(filename):
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.lower() == filename.lower():
                return os.path.join(root, file)

    # fallback path if file is missing
    return os.path.join(BASE_DIR, filename)


CH3_NODAL = find_pdf("Chapter 3 azral - Nodal Analysis.pdf")
CH4_MESH = find_pdf("Chapter 4 azral - Mesh Analysis.pdf")

FINAL_2025 = find_pdf("sfinal28575.pdf")
TEST1_2025 = find_pdf("ujian1228575.pdf")
TEST2_2025 = find_pdf("ujian1228575 (2).pdf")


class LearningModule:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.lessons = []
        self.current_lesson = 0

    def add_lesson(self, lesson):
        self.lessons.append(lesson)

    def get_current_lesson(self):
        if self.current_lesson < len(self.lessons):
            return self.lessons[self.current_lesson]
        return None

    def reset(self):
        self.current_lesson = 0


class Lesson:
    def __init__(self, title, slide_pages, example, problems):
        self.title = title
        self.slide_pages = slide_pages
        self.example = example
        self.problems = problems


def pdf_slide(title, pdf_path, page_number):
    return {
        "type": "pdf",
        "title": title,
        "pdf_path": pdf_path,
        "page_number": page_number
    }


def create_kvl_module():
    module = LearningModule(
        "Kirchhoff's Voltage Law (KVL)",
        "Study voltage law and loop equations used in DC circuit analysis."
    )

    lesson = Lesson(
        title="KVL and Loop Voltage Concept",
        slide_pages=[
            pdf_slide("KVL foundation from mesh analysis", CH4_MESH, 2),
            pdf_slide("Mesh current and loop concept", CH4_MESH, 3),
            pdf_slide("Mesh analysis steps based on KVL", CH4_MESH, 4),
            pdf_slide("KVL worked circuit example", CH4_MESH, 5),
            pdf_slide("KVL equation setup", CH4_MESH, 7),
            pdf_slide("Solving KVL equations", CH4_MESH, 8)
        ],
        example={
            "title": "Worked Example: Series KVL Circuit",
            "description": "A 24 V source is connected in series with R1 = 8 ohm and R2 = 4 ohm.",
            "circuit_def": {
                "topology": "series",
                "components": [
                    {"type": "V", "name": "V1", "value": 24},
                    {"type": "R", "name": "R1", "value": 8},
                    {"type": "R", "name": "R2", "value": 4}
                ]
            },
            "solution_steps": [
                "R_total = R1 + R2 = 8 + 4 = 12 ohm",
                "I = Vs / R_total = 24 / 12 = 2 A",
                "V_R1 = I x R1 = 2 x 8 = 16 V",
                "V_R2 = I x R2 = 2 x 4 = 8 V",
                "KVL check: -24 + 16 + 8 = 0"
            ]
        },
        problems=[
            {
                "description": "KVL Practice 1: Series voltage drop",
                "question": "Determine the voltage across R1.",
                "target_variable": "V_R1",
                "unit": "V",
                "answer": 16.0,
                "circuit_def": {
                    "topology": "series",
                    "components": [
                        {"type": "V", "name": "V1", "value": 24},
                        {"type": "R", "name": "R1", "value": 8},
                        {"type": "R", "name": "R2", "value": 4}
                    ],
                    "precalculated_solutions": {"V_R1": 16.0}
                },
                "hint": "Find total resistance, calculate current, then use V_R1 = I x R1."
            },
            {
                "description": "KVL Practice 2: Voltage divider",
                "question": "Determine the voltage across R2.",
                "target_variable": "V_R2",
                "unit": "V",
                "answer": 10.0,
                "circuit_def": {
                    "topology": "series",
                    "components": [
                        {"type": "V", "name": "V1", "value": 30},
                        {"type": "R", "name": "R1", "value": 10},
                        {"type": "R", "name": "R2", "value": 5}
                    ],
                    "precalculated_solutions": {"V_R2": 10.0}
                },
                "hint": "R_total = 15 ohm. Current = 30/15 = 2 A. Then V_R2 = 2 x 5."
            },
            {
                "description": "KVL Practice 3: Loop current",
                "question": "Determine the loop current I_total.",
                "target_variable": "I_total",
                "unit": "A",
                "answer": 3.0,
                "circuit_def": {
                    "topology": "series",
                    "components": [
                        {"type": "V", "name": "V1", "value": 18},
                        {"type": "R", "name": "R1", "value": 2},
                        {"type": "R", "name": "R2", "value": 4}
                    ],
                    "precalculated_solutions": {"I_total": 3.0}
                },
                "hint": "Use I = V / R_total."
            }
        ]
    )

    module.add_lesson(lesson)
    return module


def create_kcl_module():
    module = LearningModule(
        "Kirchhoff's Current Law (KCL)",
        "Study current law and node equations used in DC circuit analysis."
    )

    lesson = Lesson(
        title="KCL and Node Current Concept",
        slide_pages=[
            pdf_slide("Node concept", CH3_NODAL, 2),
            pdf_slide("Reference node", CH3_NODAL, 3),
            pdf_slide("KCL foundation", CH3_NODAL, 8),
            pdf_slide("Nodal analysis steps based on KCL", CH3_NODAL, 9),
            pdf_slide("KCL worked circuit example", CH3_NODAL, 10),
            pdf_slide("KCL equation setup", CH3_NODAL, 12)
        ],
        example={
            "title": "Worked Example: Parallel KCL Circuit",
            "description": "A 12 V source is connected to two parallel resistors, R1 = 6 ohm and R2 = 3 ohm.",
            "circuit_def": {
                "topology": "parallel",
                "components": [
                    {"type": "V", "name": "V1", "value": 12},
                    {"type": "R", "name": "R1", "value": 6},
                    {"type": "R", "name": "R2", "value": 3}
                ]
            },
            "solution_steps": [
                "Voltage across each branch is 12 V.",
                "I_R1 = 12 / 6 = 2 A",
                "I_R2 = 12 / 3 = 4 A",
                "I_total = I_R1 + I_R2 = 2 + 4 = 6 A",
                "KCL is satisfied because entering current equals leaving current."
            ]
        },
        problems=[
            {
                "description": "KCL Practice 1: Branch current",
                "question": "Determine the current through R2.",
                "target_variable": "I_R2",
                "unit": "A",
                "answer": 4.0,
                "circuit_def": {
                    "topology": "parallel",
                    "components": [
                        {"type": "V", "name": "V1", "value": 12},
                        {"type": "R", "name": "R1", "value": 6},
                        {"type": "R", "name": "R2", "value": 3}
                    ],
                    "precalculated_solutions": {"I_R2": 4.0}
                },
                "hint": "In parallel, voltage is the same across each branch. Use I_R2 = V/R2."
            },
            {
                "description": "KCL Practice 2: Total current",
                "question": "Determine the total current supplied by the source.",
                "target_variable": "I_total",
                "unit": "A",
                "answer": 6.0,
                "circuit_def": {
                    "topology": "parallel",
                    "components": [
                        {"type": "V", "name": "V1", "value": 12},
                        {"type": "R", "name": "R1", "value": 6},
                        {"type": "R", "name": "R2", "value": 3}
                    ],
                    "precalculated_solutions": {"I_total": 6.0}
                },
                "hint": "Find each branch current, then add them."
            },
            {
                "description": "KCL Practice 3: Three branches",
                "question": "Determine the total current supplied by the source.",
                "target_variable": "I_total",
                "unit": "A",
                "answer": 11.0,
                "circuit_def": {
                    "topology": "parallel",
                    "components": [
                        {"type": "V", "name": "V1", "value": 18},
                        {"type": "R", "name": "R1", "value": 6},
                        {"type": "R", "name": "R2", "value": 3},
                        {"type": "R", "name": "R3", "value": 9}
                    ],
                    "precalculated_solutions": {"I_total": 11.0}
                },
                "hint": "I_R1 = 18/6, I_R2 = 18/3, I_R3 = 18/9. Add all branch currents."
            }
        ]
    )

    module.add_lesson(lesson)
    return module


def create_mesh_module():
    module = LearningModule(
        "Mesh Analysis",
        "Study mesh-current analysis using uploaded lecture slides and exam questions."
    )

    lesson = Lesson(
        title="Mesh Analysis from Lecture Notes",
        slide_pages=[
            pdf_slide("Mesh analysis overview", CH4_MESH, 2),
            pdf_slide("Mesh and mesh current terms", CH4_MESH, 3),
            pdf_slide("Mesh analysis steps", CH4_MESH, 4),
            pdf_slide("Lecture worked circuit", CH4_MESH, 5),
            pdf_slide("Assign mesh currents", CH4_MESH, 6),
            pdf_slide("Apply KVL", CH4_MESH, 7),
            pdf_slide("Solve mesh equations", CH4_MESH, 8),
            pdf_slide("Mesh with current source", CH4_MESH, 14),
            pdf_slide("Supermesh concept", CH4_MESH, 19),
            pdf_slide("Supermesh worked example", CH4_MESH, 22)
        ],
        example={
            "title": "Lecture Worked Example: Mesh Analysis",
            "description": "This worked example is taken from the uploaded Mesh Analysis lecture slide.",
            "pdf_path": CH4_MESH,
            "page_number": 5,
            "solution_steps": [
                "Assign mesh currents as shown in the lecture slide.",
                "Apply KVL around each loop.",
                "For shared resistors, use the current difference between adjacent meshes.",
                "Solve the simultaneous equations."
            ]
        },
        problems=[
            {
                "description": "Final Exam 2024/2025 Question 2(b): Mesh Analysis",
                "question": "Refer to the PDF page. Determine Iy using mesh analysis.",
                "target_variable": "IY",
                "unit": "A",
                "answer": 4.286,
                "display_type": "pdf_page",
                "pdf_path": FINAL_2025,
                "page_number": 3,
                "circuit_def": {
                    "topology": "exam_reference",
                    "components": [],
                    "precalculated_solutions": {"IY": 4.286}
                },
                "hint": "Use mesh currents and KVL. Solve the simultaneous equations to get Iy."
            },
            {
                "description": "Test 2 2024/2025 Question 1: Mesh Analysis",
                "question": "Refer to the PDF page. Determine Vx using mesh analysis.",
                "target_variable": "VX",
                "unit": "V",
                "answer": 21.8,
                "display_type": "pdf_page",
                "pdf_path": TEST2_2025,
                "page_number": 2,
                "circuit_def": {
                    "topology": "exam_reference",
                    "components": [],
                    "precalculated_solutions": {"VX": 21.8}
                },
                "hint": "Assign mesh currents, write KVL equations, solve the mesh currents, then calculate Vx."
            }
        ]
    )

    module.add_lesson(lesson)
    return module


def create_nodal_module():
    module = LearningModule(
        "Nodal Analysis",
        "Study node-voltage analysis using uploaded lecture slides and exam questions."
    )

    lesson = Lesson(
        title="Nodal Analysis from Lecture Notes",
        slide_pages=[
            pdf_slide("Basic node concept", CH3_NODAL, 2),
            pdf_slide("Reference node", CH3_NODAL, 3),
            pdf_slide("KCL foundation", CH3_NODAL, 8),
            pdf_slide("Nodal analysis steps", CH3_NODAL, 9),
            pdf_slide("Lecture worked circuit", CH3_NODAL, 10),
            pdf_slide("Assign node voltages", CH3_NODAL, 11),
            pdf_slide("Apply KCL", CH3_NODAL, 12),
            pdf_slide("Solve node equations", CH3_NODAL, 13),
            pdf_slide("Nodal with voltage source", CH3_NODAL, 21),
            pdf_slide("Supernode concept", CH3_NODAL, 28)
        ],
        example={
            "title": "Lecture Worked Example: Nodal Analysis",
            "description": "This worked example is taken from the uploaded Nodal Analysis lecture slide.",
            "pdf_path": CH3_NODAL,
            "page_number": 10,
            "solution_steps": [
                "Select the reference node.",
                "Assign node voltages.",
                "Apply KCL at each non-reference node.",
                "Use Ohm's Law to express each branch current.",
                "Solve the simultaneous equations."
            ]
        },
        problems=[
            {
                "description": "Final Exam 2024/2025 Question 2(a): Nodal Analysis",
                "question": "Refer to the PDF page. Determine Ix using nodal analysis.",
                "target_variable": "IX",
                "unit": "A",
                "answer": 2.736,
                "display_type": "pdf_page",
                "pdf_path": FINAL_2025,
                "page_number": 3,
                "circuit_def": {
                    "topology": "exam_reference",
                    "components": [],
                    "precalculated_solutions": {"IX": 2.736}
                },
                "hint": "Use nodal analysis. Assign node voltages, apply KCL, solve equations, then calculate Ix."
            },
            {
                "description": "Test 1 2024/2025 Question 3: Nodal Analysis",
                "question": "Refer to the PDF page. Determine Ix using nodal analysis.",
                "target_variable": "IX",
                "unit": "A",
                "answer": 1.114,
                "display_type": "pdf_page",
                "pdf_path": TEST1_2025,
                "page_number": 3,
                "circuit_def": {
                    "topology": "exam_reference",
                    "components": [],
                    "precalculated_solutions": {"IX": 1.114}
                },
                "hint": "Use KCL at the required node and calculate Ix from the solved node voltage."
            }
        ]
    )

    module.add_lesson(lesson)
    return module


def get_all_modules():
    return {
        "kvl": create_kvl_module(),
        "kcl": create_kcl_module(),
        "mesh": create_mesh_module(),
        "nodal": create_nodal_module()
    }


# === AUTO EXTEND PRACTICE START ===

_FINAL_2025 = globals().get("FINAL_2025", find_pdf("sfinal28575.pdf"))
_TEST1_2025 = globals().get("TEST1_2025", find_pdf("ujian1228575.pdf"))
_TEST2_2025 = globals().get("TEST2_2025", find_pdf("ujian1228575 (2).pdf"))


def _series_problem(index):
    data = [
        (24, [8, 4], "V_R1"),
        (30, [10, 5], "V_R2"),
        (18, [2, 4], "I_total"),
        (36, [4, 8, 6], "V_R3"),
        (60, [5, 10, 15], "R_total"),
        (48, [6, 6, 12], "V_R2"),
        (20, [2, 3, 5], "I_total"),
        (72, [8, 10, 6], "V_R1")
    ]

    source, resistors, target = data[index]
    r_total = sum(resistors)
    current = source / r_total

    solutions = {
        "I_total": round(current, 3),
        "R_total": round(r_total, 3),
        "V_total": source
    }

    components = [{"type": "V", "name": "V1", "value": source}]

    for i, r in enumerate(resistors):
        name = "R" + str(i + 1)
        components.append({"type": "R", "name": name, "value": r})
        solutions["V_" + name] = round(current * r, 3)
        solutions["I_" + name] = round(current, 3)

    return {
        "description": "KVL Custom Practice " + str(index + 1),
        "question": "Using KVL, determine " + target + ".",
        "target_variable": target,
        "unit": "A" if target.startswith("I") else ("ohm" if target == "R_total" else "V"),
        "answer": solutions[target],
        "circuit_def": {
            "topology": "series",
            "components": components,
            "precalculated_solutions": solutions
        },
        "hint": (
            "Step 1: Identify that this is a series circuit. In series, the same current flows through all resistors.\n"
            "Step 2: Add the resistors to obtain total resistance: R_total = " + str(r_total) + " ohm.\n"
            "Step 3: Apply Ohm's Law to find loop current: I = V_total / R_total = "
            + str(source) + " / " + str(r_total) + ".\n"
            "Step 4: If the required value is voltage, use V_R = I x R. If the required value is current, use I_total."
        )
    }


def _parallel_problem(index):
    data = [
        (12, [6, 3], "I_R2"),
        (12, [6, 3], "I_total"),
        (18, [6, 3, 9], "I_total"),
        (30, [10, 15, 5], "I_R3"),
        (24, [8, 12, 6], "I_total"),
        (36, [9, 18, 6], "I_R1"),
        (20, [10, 5, 4], "I_total"),
        (48, [12, 24, 8], "I_R3")
    ]

    source, resistors, target = data[index]
    branch_currents = [source / r for r in resistors]
    total_current = sum(branch_currents)

    solutions = {
        "I_total": round(total_current, 3),
        "V_total": source
    }

    components = [{"type": "V", "name": "V1", "value": source}]

    for i, r in enumerate(resistors):
        name = "R" + str(i + 1)
        components.append({"type": "R", "name": name, "value": r})
        solutions["I_" + name] = round(branch_currents[i], 3)
        solutions["V_" + name] = source

    return {
        "description": "KCL Custom Practice " + str(index + 1),
        "question": "Using KCL, determine " + target + ".",
        "target_variable": target,
        "unit": "A",
        "answer": solutions[target],
        "circuit_def": {
            "topology": "parallel",
            "components": components,
            "precalculated_solutions": solutions
        },
        "hint": (
            "Step 1: Identify that this is a parallel circuit. In parallel, each branch has the same voltage as the source: "
            + str(source) + " V.\n"
            "Step 2: Calculate each branch current using I = V / R.\n"
            "Step 3: Apply KCL. The total source current is the sum of all branch currents.\n"
            "Step 4: If the question asks for one branch current, use that branch resistance only."
        )
    }


def _mesh_problem(index):
    data = [
        (5, 10, 10, 15, 10, "i1"),
        (4, 8, 6, 20, 12, "i2"),
        (6, 12, 9, 24, 18, "i1"),
        (3, 6, 9, 18, 12, "i2"),
        (8, 4, 12, 32, 16, "i1"),
        (10, 5, 15, 40, 20, "i2")
    ]

    r1, rs, r3, vs1, vs2, target = data[index]

    a = r1 + rs
    b = -rs
    c = -rs
    d = r3 + rs

    det = a * d - b * c
    i1 = (vs1 * d - b * vs2) / det
    i2 = (a * vs2 - c * vs1) / det

    solutions = {
        "i1": round(i1, 3),
        "i2": round(i2, 3)
    }

    return {
        "description": "Mesh Custom Practice " + str(index + 1),
        "question": "Using mesh analysis, determine " + target + ".",
        "target_variable": target,
        "unit": "A",
        "answer": solutions[target],
        "display_type": "custom_diagram",
        "diagram_type": "mesh_two_loop",
        "diagram_title": "Two-Loop Mesh Circuit",
        "top_left": "R1 = " + str(r1) + " ohm",
        "shared": "R2 = " + str(rs) + " ohm",
        "top_right": "R3 = " + str(r3) + " ohm",
        "left_source": "Vs1 = " + str(vs1) + " V",
        "right_source": "Vs2 = " + str(vs2) + " V",
        "diagram_note": (
            "Equation 1: (" + str(r1) + " + " + str(rs) + ")i1 - "
            + str(rs) + "i2 = " + str(vs1) + ".   "
            "Equation 2: -" + str(rs) + "i1 + (" + str(r3) + " + "
            + str(rs) + ")i2 = " + str(vs2) + "."
        ),
        "circuit_def": {
            "topology": "custom_mesh",
            "components": [],
            "precalculated_solutions": solutions
        },
        "hint": (
            "Step 1: Assign clockwise mesh currents i1 and i2.\n"
            "Step 2: For the shared resistor, use the current difference between meshes.\n"
            "Step 3: Write KVL for mesh 1: (" + str(r1) + " + " + str(rs) + ")i1 - "
            + str(rs) + "i2 = " + str(vs1) + ".\n"
            "Step 4: Write KVL for mesh 2: -" + str(rs) + "i1 + (" + str(r3) + " + "
            + str(rs) + ")i2 = " + str(vs2) + ".\n"
            "Step 5: Solve both equations simultaneously to obtain " + target + "."
        )
    }


def _nodal_problem(index):
    data = [
        (24, 6, 12, 1, "V_node_1"),
        (18, 3, 6, 2, "V_node_1"),
        (30, 10, 5, 1, "V_node_1"),
        (20, 4, 8, 2, "V_node_1"),
        (36, 9, 6, 1, "V_node_1"),
        (12, 2, 4, 3, "V_node_1")
    ]

    vs, r1, r2, current_source, target = data[index]

    v1 = (current_source + (vs / r1)) / ((1 / r1) + (1 / r2))
    solutions = {
        "V_node_1": round(v1, 3)
    }

    return {
        "description": "Nodal Custom Practice " + str(index + 1),
        "question": "Using nodal analysis, determine V1.",
        "target_variable": target,
        "unit": "V",
        "answer": solutions[target],
        "display_type": "custom_diagram",
        "diagram_type": "nodal_one_node",
        "diagram_title": "Single-Node Nodal Circuit",
        "source_label": "Vs = " + str(vs) + " V",
        "left_resistor": "R1 = " + str(r1) + " ohm",
        "middle_resistor": "R2 = " + str(r2) + " ohm",
        "current_label": "I1 = " + str(current_source) + " A",
        "diagram_note": (
            "KCL equation: (V1 - " + str(vs) + ")/" + str(r1)
            + " + V1/" + str(r2) + " = " + str(current_source) + "."
        ),
        "circuit_def": {
            "topology": "custom_nodal",
            "components": [],
            "precalculated_solutions": solutions
        },
        "hint": (
            "Step 1: Select the bottom line as the reference node.\n"
            "Step 2: Label the main node voltage as V1.\n"
            "Step 3: Express current through R1 as (V1 - Vs) / R1.\n"
            "Step 4: Express current through R2 as V1 / R2.\n"
            "Step 5: Apply KCL: current leaving through resistors equals current entering from source.\n"
            "Step 6: Solve: (V1 - " + str(vs) + ")/" + str(r1)
            + " + V1/" + str(r2) + " = " + str(current_source) + "."
        )
    }


def _exam_problem(description, question, target, unit, answer, pdf_path, page_number, hint):
    return {
        "description": description,
        "question": question,
        "target_variable": target,
        "unit": unit,
        "answer": answer,
        "display_type": "pdf_page",
        "pdf_path": pdf_path,
        "page_number": page_number,
        "circuit_def": {
            "topology": "exam_reference",
            "components": [],
            "precalculated_solutions": {
                target: answer
            }
        },
        "hint": hint
    }


_original_get_all_modules_for_practice = get_all_modules


def get_all_modules():
    modules = _original_get_all_modules_for_practice()

    kvl_exam = [
        _exam_problem(
            "KVL-Based Exam Practice: Final Exam Mesh Question",
            "Refer to the PDF page. Determine Iy. This question uses KVL through mesh analysis.",
            "IY",
            "A",
            4.286,
            _FINAL_2025,
            3,
            "This is an exam-style KVL application. Assign mesh currents, apply KVL around each loop, form simultaneous equations, and solve for Iy."
        ),
        _exam_problem(
            "KVL-Based Exam Practice: Test Question",
            "Refer to the PDF page. Determine Vx using KVL/mesh analysis.",
            "VX",
            "V",
            21.8,
            _TEST2_2025,
            2,
            "Use loop equations. Assign mesh currents first, then calculate the voltage Vx from the solved current."
        )
    ]

    kcl_exam = [
        _exam_problem(
            "KCL-Based Exam Practice: Final Exam Nodal Question",
            "Refer to the PDF page. Determine Ix. This question uses KCL through nodal analysis.",
            "IX",
            "A",
            2.736,
            _FINAL_2025,
            3,
            "This is an exam-style KCL application. Assign node voltages, apply KCL at each node, solve the equations, and calculate Ix."
        ),
        _exam_problem(
            "KCL-Based Exam Practice: Test Question",
            "Refer to the PDF page. Determine Ix using KCL/nodal analysis.",
            "IX",
            "A",
            1.114,
            _TEST1_2025,
            3,
            "Apply KCL at the required node. After solving the node voltage, calculate Ix using Ohm's Law."
        )
    ]

    modules["kvl"].lessons[0].problems = [_series_problem(i) for i in range(8)] + kvl_exam
    modules["kcl"].lessons[0].problems = [_parallel_problem(i) for i in range(8)] + kcl_exam

    mesh_existing = modules["mesh"].lessons[0].problems
    mesh_exam = [p for p in mesh_existing if p.get("display_type") == "pdf_page"]
    modules["mesh"].lessons[0].problems = [_mesh_problem(i) for i in range(6)] + mesh_exam[:2]

    nodal_existing = modules["nodal"].lessons[0].problems
    nodal_exam = [p for p in nodal_existing if p.get("display_type") == "pdf_page"]
    modules["nodal"].lessons[0].problems = [_nodal_problem(i) for i in range(6)] + nodal_exam[:2]

    return modules

# === AUTO EXTEND PRACTICE END ===

