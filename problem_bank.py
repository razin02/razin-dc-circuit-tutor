import random

TEXTBOOK_PROBLEMS = {
    'easy': [
        {
            'description': "Textbook KVL Example: A single loop circuit with a 24V DC voltage source and two series resistors (8Ω and 4Ω).",
            'question': "What is the voltage drop across the 8Ω resistor (V_R1) in Volts?",
            'target_variable': 'V_R1',
            'unit': 'V',
            'circuit_def': {
                'topology': 'series',
                'components': [
                    {'type': 'V', 'name': 'V1', 'value': 24},
                    {'type': 'R', 'name': 'R1', 'value': 8},
                    {'type': 'R', 'name': 'R2', 'value': 4}
                ],
                'precalculated_solutions': {
                    'I_total': 2.0,
                    'R_total': 12.0,
                    'V_total': 24.0,
                    'V_R1': 16.0,
                    'I_R1': 2.0,
                    'V_R2': 8.0,
                    'I_R2': 2.0
                }
            },
            'hint': (
                "Step 1: The total resistance in a series loop is: R_total = R1 + R2 = 8Ω + 4Ω = 12Ω.\n"
                "Step 2: Using Ohm's Law, find the loop current: I = V1 / R_total = 24V / 12Ω = 2A.\n"
                "Step 3: Find the voltage drop across R1: V_R1 = I * R1 = 2A * 8Ω = 16V."
            )
        },
        {
            'description': "Textbook KCL Example: A parallel circuit with a 12V voltage source and two parallel resistors (6Ω and 3Ω).",
            'question': "What is the current flowing through the 3Ω resistor (I_R2) in Amperes?",
            'target_variable': 'I_R2',
            'unit': 'A',
            'circuit_def': {
                'topology': 'parallel',
                'components': [
                    {'type': 'V', 'name': 'V1', 'value': 12},
                    {'type': 'R', 'name': 'R1', 'value': 6},
                    {'type': 'R', 'name': 'R2', 'value': 3}
                ],
                'precalculated_solutions': {
                    'I_total': 6.0,
                    'R_total': 2.0,
                    'V_total': 12.0,
                    'V_R1': 12.0,
                    'I_R1': 2.0,
                    'V_R2': 12.0,
                    'I_R2': 4.0
                }
            },
            'hint': (
                "Step 1: In a parallel circuit, the voltage across all branches is the same as the source voltage: V = 12V.\n"
                "Step 2: Use Ohm's Law to find the current through R2 (3Ω): I_R2 = V / R2 = 12V / 3Ω = 4A."
            )
        },
        {
            'description': "Nodal Analysis Slide Example: A single non-reference node V1 connected to a 24V DC voltage source through a 6Ω resistor, a 12Ω resistor to ground, and a 1A current source entering the node.",
            'question': "Calculate the node voltage V1 in Volts.",
            'target_variable': 'V_node_1',
            'unit': 'V',
            'circuit_def': {
                'topology': 'custom_nodal',
                'components': [
                    {'type': 'V', 'name': 'V1', 'value': 24},
                    {'type': 'R', 'name': 'R1', 'value': 6},
                    {'type': 'R', 'name': 'R2', 'value': 12},
                    {'type': 'I', 'name': 'I1', 'value': 1}
                ],
                'precalculated_solutions': {
                    'V_node_1': 20.0
                }
            },
            'hint': (
                "Step 1: Apply KCL at node V1. Set sum of leaving currents equal to entering currents:\n"
                "       (V1 - 24) / 6 + V1 / 12 = 1\n"
                "Step 2: Multiply the entire equation by 12 to clear the denominators:\n"
                "       2 * (V1 - 24) + V1 = 12\n"
                "       2 * V1 - 48 + V1 = 12\n"
                "       3 * V1 = 60\n"
                "Step 3: Solve for V1:\n"
                "       V1 = 20V."
            )
        }
    ],
    'medium': [
        {
            'description': "Mesh Analysis Slide Example: A two-loop circuit. Loop 1 has a 15V source, a 5Ω resistor, and a shared 10Ω resistor with a 10V source. Loop 2 has the 10V source, the shared 10Ω resistor, a 6Ω resistor, and a 4Ω resistor.",
            'question': "Using mesh analysis, find the clockwise mesh current i1 in Amperes.",
            'target_variable': 'i1',
            'unit': 'A',
            'circuit_def': {
                'topology': 'custom_mesh',
                'components': [],
                'precalculated_solutions': {
                    'i1': 1.0,
                    'i2': 1.0,
                    'i3': 0.0
                }
            },
            'hint': (
                "Step 1: Apply KVL to Mesh 1 with clockwise current i1:\n"
                "       -15 + 5*i1 + 10*(i1 - i2) + 10 = 0  =>  15*i1 - 10*i2 = 5\n"
                "Step 2: Apply KVL to Mesh 2 with clockwise current i2:\n"
                "       -10 + 10*(i2 - i1) + 6*i2 + 4*i2 = 0  =>  -10*i1 + 20*i2 = 10\n"
                "Step 3: Solve the simultaneous equations:\n"
                "       From Mesh 1: 3*i1 - 2*i2 = 1\n"
                "       From Mesh 2: -i1 + 2*i2 = 1\n"
                "       Adding both equations: 2*i1 = 2  =>  i1 = 1A."
            )
        },
        {
            'description': "Supermesh Slide Example: A two-loop circuit with a 20V voltage source, a 6Ω resistor, a 4Ω resistor, a 2Ω resistor, a 12V voltage source, and a shared 4A current source between the meshes.",
            'question': "Find the mesh current I1 (loop 1) in Amperes.",
            'target_variable': 'I1',
            'unit': 'A',
            'circuit_def': {
                'topology': 'custom_supermesh',
                'components': [],
                'precalculated_solutions': {
                    'I1': 3.33,
                    'I2': -0.67
                }
            },
            'hint': (
                "Step 1: Create a supermesh by removing the shared 4A current source from KVL equations.\n"
                "Step 2: Apply KVL around the supermesh loop:\n"
                "       -20 + 6*I1 + 4*I1 + 2*I2 - 12 = 0  =>  10*I1 + 2*I2 = 32\n"
                "Step 3: Write the current source constraint equation:\n"
                "       The current source is between the loops, pointing upwards: I1 - I2 = 4  =>  I2 = I1 - 4\n"
                "Step 4: Substitute and solve:\n"
                "       10*I1 + 2*(I1 - 4) = 32\n"
                "       12*I1 - 8 = 32  =>  12*I1 = 40  =>  I1 = 3.33A."
            )
        }
    ],
    'hard': [
        {
            'description': "Supernode Slide Example: A circuit with two non-reference nodes. An independent 12V voltage source is connected between node 1 and node 2 (positive terminal at node 1). Resistors to ground are R1 = 4Ω (node 1) and R2 = 2Ω (node 2). A 6A current source enters node 1, and a 4A current source enters node 2.",
            'question': "Find the node voltage V1 in Volts using the concept of a supernode.",
            'target_variable': 'V1',
            'unit': 'V',
            'circuit_def': {
                'topology': 'custom_supernode',
                'components': [],
                'precalculated_solutions': {
                    'V1': 10.67,
                    'V2': -1.33
                }
            },
            'hint': (
                "Step 1: Enclose the 12V voltage source in a supernode between nodes 1 and 2.\n"
                "Step 2: Apply KCL at the supernode (sum of entering currents = sum of leaving currents):\n"
                "       6 + 4 = V1 / 4 + V2 / 2  =>  2 = 0.25*V1 + 0.5*V2 (after simplifying)\n"
                "Step 3: Write the constraint equation for the 12V source:\n"
                "       V1 - V2 = 12  =>  V2 = V1 - 12\n"
                "Step 4: Substitute and solve:\n"
                "       2 = 0.25*V1 + 0.5*(V1 - 12)\n"
                "       2 = 0.75*V1 - 6\n"
                "       0.75*V1 = 8  =>  V1 = 10.67V."
            )
        }
    ]
}

class ProblemBank:
    def __init__(self):
        self.problem_counter = 0

    def generate_problem(self, difficulty='easy', topology=None):
        self.problem_counter += 1
        
        # 1. Prioritize slide-specific textbook problems if available
        # Avoid indexing out of bounds if problem_counter gets large
        if difficulty in TEXTBOOK_PROBLEMS and len(TEXTBOOK_PROBLEMS[difficulty]) > 0:
            # We want to cycle through them based on problem_counter
            prob_index = (self.problem_counter - 1) % len(TEXTBOOK_PROBLEMS[difficulty])
            
            # Check if this textbook problem fits the requested topology filter
            prob_data = TEXTBOOK_PROBLEMS[difficulty][prob_index]
            if topology is None or prob_data['circuit_def']['topology'] == topology:
                problem = {
                    'id': self.problem_counter,
                    'difficulty': difficulty,
                    'circuit_def': prob_data['circuit_def'],
                    'topology': prob_data['circuit_def']['topology'],
                    'description': prob_data['description'],
                    'question': prob_data['question'],
                    'target_variable': prob_data['target_variable'],
                    'unit': prob_data['unit'],
                    'hint': prob_data['hint']
                }
                return problem

        # 2. Fallback to procedural generation if topology mismatch or all completed
        if topology is None:
            topology = random.choice(['series', 'parallel'])
            
        # Determine number of resistors based on difficulty
        if difficulty == 'easy':
            num_resistors = 2
            v_range = (5, 12)
            r_range = (1, 10)
        elif difficulty == 'medium':
            num_resistors = 3
            v_range = (10, 24)
            r_range = (2, 20)
        else: # hard
            num_resistors = 4
            v_range = (20, 50)
            r_range = (5, 50)
            
        from logic.circuit_solver import CircuitSolver
        solver = CircuitSolver()
        
        # Retry logic: Generate until we have a valid circuit without short/open errors
        attempts = 0
        while attempts < 10:
            attempts += 1
            # Random values
            v_val = random.randint(*v_range)
            # Only generate Resistors
            comp_types = ['R'] * num_resistors

            resistors = []
            for i, t in enumerate(comp_types):
                val = random.randint(*r_range)
                resistors.append({'type': t, 'name': f'{t}{i+1}', 'value': val})
            
            circuit_def = {
                'topology': topology,
                'components': [{'type': 'V', 'name': 'V1', 'value': v_val}] + resistors
            }
            
            solution = solver.solve_circuit(circuit_def)
            if 'error' not in solution:
                break # Valid circuit
            
        if 'error' in solution:
            # Fallback to extremely simple series if still failing
            circuit_def = {
                'topology': 'series',
                'components': [
                    {'type': 'V', 'name': 'V1', 'value': 10},
                    {'type': 'R', 'name': 'R1', 'value': 10}
                ]
            }
            solution = solver.solve_circuit(circuit_def)
            resistors = [circuit_def['components'][1]]
        
        # Choose question type
        q_options = ['total_current', 'total_resistance']
        for r in resistors:
            q_options.append(f'voltage_{r["name"]}')
            q_options.append(f'current_{r["name"]}')
            
        q_type = random.choice(q_options)
        
        problem = {
            'id': self.problem_counter,
            'difficulty': difficulty,
            'circuit_def': circuit_def,
            'topology': topology
        }
        
        if q_type == 'total_current':
            problem.update({
                'description': f'Calculate the total current in this {topology} circuit.',
                'question': 'What is the total current (I_total) in Amperes?',
                'target_variable': 'I_total',
                'unit': 'A'
            })
            hint = self._generate_total_current_hint(circuit_def, solution)
        elif q_type == 'total_resistance':
            problem.update({
                'description': f'Calculate the equivalent total resistance of this {topology} circuit.',
                'question': 'What is the total resistance (R_total) in Ohms?',
                'target_variable': 'R_total',
                'unit': 'Ω'
            })
            hint = self._generate_total_resistance_hint(circuit_def, solution)
        elif q_type.startswith('voltage_'):
            r_name = q_type.split('_')[1]
            problem.update({
                'description': f'Find the voltage drop across {r_name}.',
                'question': f'What is the voltage across {r_name} (V_{r_name}) in Volts?',
                'target_variable': f'V_{r_name}',
                'unit': 'V'
            })
            hint = self._generate_component_hint(circuit_def, solution, r_name, 'voltage')
        else: # current_X
            r_name = q_type.split('_')[1]
            problem.update({
                'description': f'Find the current flowing through {r_name}.',
                'question': f'What is the current through {r_name} (I_{r_name}) in Amperes?',
                'target_variable': f'I_{r_name}',
                'unit': 'A'
            })
            hint = self._generate_component_hint(circuit_def, solution, r_name, 'current')
            
        problem['hint'] = hint
        return problem

    def _generate_total_resistance_hint(self, circuit_def, solution):
        topology = circuit_def['topology']
        resistors = [c for c in circuit_def['components'] if c['type'] == 'R']
        
        steps = []
        
        if topology == 'series':
            steps.append("\nTotal resistance in series is the sum of all components:")
            expr_parts = []
            for r in resistors: expr_parts.append(f"{r['value']}Ω")
            
            steps.append(f"R_total = {' + '.join(expr_parts)}")
            steps.append("\nCompute the sum to find the answer.")
        else: # parallel
            steps.append("\nTotal resistance in parallel uses the reciprocal formula:")
            expr_parts = []
            for r in resistors: expr_parts.append(f"1/{r['value']}")
            
            steps.append(f"1/R_total = {' + '.join(expr_parts)}")
            steps.append("\nCalculate the sum, then take the reciprocal to find R_total.")
                
        return "\n".join(steps)

    def _generate_total_current_hint(self, circuit_def, solution):
        v = solution['V_total']
        steps = [
            "Use Ohm's Law: I = V / R",
            f"V_total = {v}V",
            "1. Calculate R_total first.",
            "2. Then I_total = V_total / R_total",
            "\nPerform the division to find the total current."
        ]
        return "\n".join(steps)

    def _generate_component_hint(self, circuit_def, solution, r_name, p_type):
        topology = circuit_def['topology']
        comp = next(c for c in circuit_def['components'] if c['name']==r_name)
        
        if topology == 'series':
            if p_type == 'voltage':
                hint = f"In series, current (I) is the same through all components.\n1. Find I_total = V_total / R_total\n2. Apply V = I * R"
                return hint
            else:
                return f"In series, the current through any component is equal to the total current (I_total).\nFind I_total = V_total / R_total."
        else: # parallel
            v = solution['V_total']
            if p_type == 'voltage':
                return f"In parallel, the voltage across each branch is equal to the source voltage ({v}V)."
            else:
                return f"In parallel, each branch has the same voltage ({v}V).\nApply Ohm's Law (I = V / R) to find the branch current."

    def get_problem(self, problem_id):
        return self.generate_problem()

    def get_all_problems(self):
        return []
