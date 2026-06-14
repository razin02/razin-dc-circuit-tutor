# -*- coding: utf-8 -*-
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSET_DIR = os.path.join(BASE_DIR, "assets")
if not os.path.exists(ASSET_DIR):
    ASSET_DIR = os.path.join(BASE_DIR, "assests")

EXAM_DIR = os.path.join(ASSET_DIR, "exams")


EXAM_PROBLEMS = [
    {
        "description": "Exam Question: Nodal Analysis",
        "question": "Refer to the PDF page. Determine Ix using nodal analysis.",
        "target_variable": "IX",
        "unit": "A",
        "display_type": "pdf_page",
        "pdf_path": os.path.join(EXAM_DIR, "sfinal28575.pdf"),
        "page_number": 3,
        "circuit_def": {
            "topology": "exam_reference",
            "components": [],
            "precalculated_solutions": {
                "IX": 2.736
            }
        },
        "hint": "Use nodal analysis. Assign node voltages, apply KCL, solve the equations, then calculate IX."
    },
    {
        "description": "Exam Question: Mesh Analysis",
        "question": "Refer to the PDF page. Determine Iy using mesh analysis.",
        "target_variable": "IY",
        "unit": "A",
        "display_type": "pdf_page",
        "pdf_path": os.path.join(EXAM_DIR, "sfinal28575.pdf"),
        "page_number": 3,
        "circuit_def": {
            "topology": "exam_reference",
            "components": [],
            "precalculated_solutions": {
                "IY": 4.286
            }
        },
        "hint": "Use mesh analysis. Assign mesh currents, write KVL equations, and solve for IY."
    }
]


TEXTBOOK_PROBLEMS = {
    "easy": [
        {
            "description": "Textbook KVL Example: A single loop circuit with a 24V source and two series resistors.",
            "question": "What is the voltage drop across R1 in Volts?",
            "target_variable": "V_R1",
            "unit": "V",
            "circuit_def": {
                "topology": "series",
                "components": [
                    {"type": "V", "name": "V1", "value": 24},
                    {"type": "R", "name": "R1", "value": 8},
                    {"type": "R", "name": "R2", "value": 4}
                ],
                "precalculated_solutions": {
                    "I_total": 2.0,
                    "R_total": 12.0,
                    "V_total": 24.0,
                    "V_R1": 16.0,
                    "I_R1": 2.0,
                    "V_R2": 8.0,
                    "I_R2": 2.0
                }
            },
            "hint": "Find total resistance first, then use I = V/R and V_R1 = I x R1."
        },
        {
            "description": "Textbook KCL Example: A parallel circuit with a 12V source and two parallel resistors.",
            "question": "What is the current through R2 in Amperes?",
            "target_variable": "I_R2",
            "unit": "A",
            "circuit_def": {
                "topology": "parallel",
                "components": [
                    {"type": "V", "name": "V1", "value": 12},
                    {"type": "R", "name": "R1", "value": 6},
                    {"type": "R", "name": "R2", "value": 3}
                ],
                "precalculated_solutions": {
                    "I_total": 6.0,
                    "R_total": 2.0,
                    "V_total": 12.0,
                    "V_R1": 12.0,
                    "I_R1": 2.0,
                    "V_R2": 12.0,
                    "I_R2": 4.0
                }
            },
            "hint": "In parallel, voltage is the same across every branch. Use I_R2 = V/R2."
        }
    ],
    "medium": [],
    "hard": []
}


class ProblemBank:
    def __init__(self):
        self.problem_counter = 0

    def generate_problem(self, difficulty="easy", topology=None, topic=None):
        self.problem_counter += 1

        # 25 percent chance to show exam-style PDF problem in Tutor Mode
        if random.random() < 0.25 and topology is None and topic is None:
            exam_problem = random.choice(EXAM_PROBLEMS).copy()
            exam_problem["id"] = self.problem_counter
            exam_problem["difficulty"] = difficulty
            return exam_problem

        # Tutor Mode only uses drawable topologies
        if topology is None:
            topology = random.choice(["series", "parallel"])

        if difficulty == "easy":
            num_resistors = 2
            v_range = (5, 12)
            r_range = (1, 10)
        elif difficulty == "medium":
            num_resistors = 3
            v_range = (10, 24)
            r_range = (2, 20)
        else:
            num_resistors = 4
            v_range = (20, 50)
            r_range = (5, 50)

        from logic.circuit_solver import CircuitSolver
        solver = CircuitSolver()

        v_val = random.randint(*v_range)
        resistors = []

        for i in range(num_resistors):
            resistors.append({
                "type": "R",
                "name": "R" + str(i + 1),
                "value": random.randint(*r_range)
            })

        circuit_def = {
            "topology": topology,
            "components": [{"type": "V", "name": "V1", "value": v_val}] + resistors
        }

        solution = solver.solve_circuit(circuit_def)

        if "error" in solution:
            circuit_def = {
                "topology": "series",
                "components": [
                    {"type": "V", "name": "V1", "value": 10},
                    {"type": "R", "name": "R1", "value": 10}
                ]
            }
            solution = solver.solve_circuit(circuit_def)
            resistors = [circuit_def["components"][1]]

        q_options = ["total_current", "total_resistance"]

        for r in resistors:
            q_options.append("voltage_" + r["name"])
            q_options.append("current_" + r["name"])

        q_type = random.choice(q_options)

        problem = {
            "id": self.problem_counter,
            "difficulty": difficulty,
            "circuit_def": circuit_def,
            "topology": topology
        }

        if q_type == "total_current":
            problem.update({
                "description": "Calculate the total current in this " + topology + " circuit.",
                "question": "What is the total current I_total in Amperes?",
                "target_variable": "I_total",
                "unit": "A"
            })
            hint = self._generate_total_current_hint(circuit_def, solution)

        elif q_type == "total_resistance":
            problem.update({
                "description": "Calculate the equivalent total resistance of this " + topology + " circuit.",
                "question": "What is the total resistance R_total in Ohms?",
                "target_variable": "R_total",
                "unit": "ohm"
            })
            hint = self._generate_total_resistance_hint(circuit_def, solution)

        elif q_type.startswith("voltage_"):
            r_name = q_type.split("_")[1]
            problem.update({
                "description": "Find the voltage drop across " + r_name + ".",
                "question": "What is the voltage across " + r_name + " in Volts?",
                "target_variable": "V_" + r_name,
                "unit": "V"
            })
            hint = self._generate_component_hint(
                circuit_def, solution, r_name, "voltage")

        else:
            r_name = q_type.split("_")[1]
            problem.update({
                "description": "Find the current flowing through " + r_name + ".",
                "question": "What is the current through " + r_name + " in Amperes?",
                "target_variable": "I_" + r_name,
                "unit": "A"
            })
            hint = self._generate_component_hint(
                circuit_def, solution, r_name, "current")

        problem["hint"] = hint
        return problem

    def _generate_total_resistance_hint(self, circuit_def, solution):
        topology = circuit_def["topology"]
        resistors = [c for c in circuit_def["components"] if c["type"] == "R"]

        steps = []

        if topology == "series":
            steps.append(
                "Total resistance in series is the sum of all resistors.")
            expr_parts = [str(r["value"]) + " ohm" for r in resistors]
            steps.append("R_total = " + " + ".join(expr_parts))
        else:
            steps.append(
                "Total resistance in parallel uses the reciprocal formula.")
            expr_parts = ["1/" + str(r["value"]) for r in resistors]
            steps.append("1/R_total = " + " + ".join(expr_parts))

        return chr(10).join(steps)

    def _generate_total_current_hint(self, circuit_def, solution):
        v = solution.get("V_total", "")
        steps = [
            "Use Ohm's Law: I = V/R.",
            "V_total = " + str(v) + " V.",
            "Calculate R_total first.",
            "Then calculate I_total = V_total/R_total."
        ]
        return chr(10).join(steps)

    def _generate_component_hint(self, circuit_def, solution, r_name, p_type):
        topology = circuit_def["topology"]

        if topology == "series":
            if p_type == "voltage":
                return "In series, same current flows through all resistors. Find I_total first, then use V = I x R."
            return "In series, current through each resistor is equal to I_total."

        v = solution.get("V_total", "")

        if p_type == "voltage":
            return "In parallel, voltage across each branch is equal to the source voltage: " + str(v) + " V."

        return "In parallel, each branch has the same voltage. Use I = V/R."

    def get_problem(self, problem_id):
        return self.generate_problem()

    def get_all_problems(self):
        return []
