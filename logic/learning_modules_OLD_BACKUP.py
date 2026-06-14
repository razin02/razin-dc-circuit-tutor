"""
Learning Modules for DC Circuit Analysis
Provides structured lessons and problems.
Adapted from "Fundamentals of Electric Circuits" (Alexander & Sadiku)
"""


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

    def next_lesson(self):
        if self.current_lesson < len(self.lessons) - 1:
            self.current_lesson += 1
            return True
        return False

    def previous_lesson(self):
        if self.current_lesson > 0:
            self.current_lesson -= 1
            return True
        return False

    def reset(self):
        self.current_lesson = 0


class Lesson:
    def __init__(self, title, theory_slides, example, problems, video_url=None):
        self.title = title
        self.theory_slides = theory_slides  # List of strings (slides)
        self.example = example  # Worked example
        self.problems = problems  # List of practice problems
        self.video_url = video_url


def create_circuit_elements_lesson():
    """Create the fundamental Circuit Elements & Power lesson shared across modules"""
    return Lesson(
        title="Circuit Elements & Power",
        theory_slides=[
            """# Introduction to Circuit Elements

An **electrical element** is the core component from which all complex electric circuits are constructed. An electric circuit is simply an interconnection of these basic elements.

### Two Major Classifications:
1. **Passive Elements**: Elements that do not generate electric energy. They absorb, dissipate, or temporarily store energy.
   * *Examples:* Resistors, capacitors, and inductors.
2. **Active Elements**: Elements capable of generating and delivering electrical energy to the circuit.
   * *Examples:* Generators, batteries, operational amplifiers, and ideal voltage/current sources.

> [!NOTE]
> In this DC resistive course, we focus exclusively on **Resistors** as our passive element, and **independent/dependent sources** as our active elements.""",

            """# Power and Sign Conventions

**Power ($p$)** is the time rate at which energy ($w$) is delivered to or absorbed by a circuit element. Its standard unit is the Watt (W).
* **Instantaneous Power:** p = v x i

### The Passive Sign Convention (PSC):
To correctly analyze power in a circuit, we must adopt a consistent reference polarity:
1. **Power Absorbed ($p > 0$):**
   When the current ($i$) flows **into the positive polarity terminal** of a component.
   p = v x i
2. **Power Supplied ($p < 0$):**
   When the current ($i$) flows **out of the positive polarity terminal** (entering the negative terminal).
   p = -v x i

> [!IMPORTANT]
> **Conservation of Energy:**
> The law of conservation of energy dictates that the total power supplied in a closed system must exactly equal the total power absorbed:
> \\sum p = 0""",

            """# Active Sources: Independent vs. Dependent

Active sources generally deliver power to the circuit connected to them. They are classified into two groups:

### 1. Independent Sources
An active source whose output value (voltage or current) is **completely independent** of all other variables in the circuit.
* **Independent Voltage Source:** Delivers whatever current is necessary to maintain its specified voltage across its terminals.
* **Independent Current Source:** Delivers whatever voltage is necessary to maintain its specified current flow.

### 2. Dependent (Controlled) Sources
An active element in which the source value (voltage or current) is controlled by another voltage or current elsewhere in the circuit. These are represented by **diamond-shaped** symbols:
* **VCVS:** Voltage-Controlled Voltage Source, $v = a x v_x$
* **CCVS:** Current-Controlled Voltage Source, $v = b x i_x$
* **VCCS:** Voltage-Controlled Current Source, $i = g x v_x$
* **CCCS:** Current-Controlled Current Source, $i = h x i_x$"""
        ],
        example={
            'title': 'Worked Example: Power Calculations (PSC)',
            'description': 'Textbook Application: Calculate the power supplied or absorbed by each element in the series-parallel network shown on the left.',
            'circuit_def': {
                'topology': 'elements',
                'components': []  # Handled specially by elements drawer
            },
            'solution_steps': [
                'Step 1: Identify all given voltages, currents, and source types:',
                '        - Source V_1 (left) is a 20V independent source with current I = 5A leaving its top (+).',
                '        - Element 2 (middle) is a 12V passive element with 5A entering its top (+).',
                '        - Element 3 (right-middle) is an 8V passive element with 6A entering its top (+).',
                '        - Source 4 (right-most) is a 0.2I dependent current source (controlled by I = 5A).',
                'Step 2: Calculate power p_1 for the 20V independent voltage source:',
                '        - The 5A current flows OUT of the positive terminal.',
                '        - p_1 = -v x i = -20 x 5 = -100 W  (Power is Supplied)',
                'Step 3: Calculate power p_2 for the 12V passive element:',
                '        - The 5A current flows INTO the positive terminal.',
                '        - p_2 = v x i = 12 x 5 = 60 W  (Power is Absorbed)',
                'Step 4: Calculate power p_3 for the 8V passive element:',
                '        - The 6A current flows INTO the positive terminal.',
                '        - p_3 = v x i = 8 x 6 = 48 W  (Power is Absorbed)',
                'Step 5: Calculate power p_4 for the dependent current source (0.2I):',
                '        - Current value: i_s = 0.2 x I = 0.2 x 5 = 1 A',
                '        - The 1A current flows OUT of the positive terminal (flowing upwards).',
                '        - p_4 = -v x i = -8 x 1 = -8 W  (Power is Supplied)',
                'Step 6: Verify the conservation of energy (sum of all power = 0):',
                '        - Sum = p_1 + p_2 + p_3 + p_4',
                '        - Sum = -100 + 60 + 48 - 8 = 0 W',
                '        - The sum is exactly 0 W! Energy is perfectly conserved.'
            ]
        },
        problems=[],
        video_url="https://www.youtube.com/watch?v=J3sN2N-Uskc"
    )


def create_kvl_module():
    """Create Kirchhoff's Voltage Law learning module"""
    module = LearningModule(
        "Kirchhoff's Voltage Law (KVL)",
        "Learn how to apply KVL to analyze circuit loops based on textbook fundamentals."
    )

    # Lesson 1: Circuit Elements & Power
    module.add_lesson(create_circuit_elements_lesson())

    # Lesson 2: Kirchhoff's Voltage Law
    lesson2 = Lesson(
        title="Kirchhoff's Voltage Law",
        theory_slides=[
            """# Kirchhoff's Voltage Law (KVL)

**Kirchhoff's Voltage Law (KVL)** is a fundamental principle based on the law of **conservation of energy**. It states:
> The algebraic sum of all voltages around any closed path (or loop) in a circuit is equal to zero.

### Mathematical Equation:
\\sum_{m=1}^{M} v_m = 0
where $M$ is the number of voltages in the loop and $v_m$ is the voltage of the $m$-th element.

### Sign Convention Strategy:
To apply KVL, choose an arbitrary loop direction (e.g., clockwise) and follow the path:
1. If you enter the **negative ($-$ ) terminal** of an element first, record its value as negative: -v.
2. If you enter the **positive ($+$) terminal** of an element first, record its value as positive: +v.

> [!TIP]
> Whichever traversing direction you pick, keep it consistent for the entire loop calculation!""",

            """# Loop Traversing Rules in Action

Consider a simple closed series loop with a voltage source and multiple resistors. Let's trace it step-by-step:

1. **Assign a Clockwise Current ($i$):**
   The current flows out of the source, through the resistors, and returns to the source.
2. **Write Voltage Drops Across Resistors:**
   Using Ohm's Law ($v = i * R$), the voltage across each resistor will be positive in the direction of current flow.
3. **KVL Equation Formulation:**
   Traced clockwise:
   -V_source + v_1 + v_2 = 0
   -V_source + (i * R_1) + (i * R_2) = 0

> [!NOTE]
> This leads directly to the formulation of equivalent series resistance:
> R_{eq} = R_1 + R_2""",

            """# The Voltage Divider Rule (VDR)

When resistors are connected in **series**, the total source voltage is divided among them in direct proportion to their resistance values.

### The KVL-Derived Equation:
Since the same current ($i$) flows through all components in a series path:
i = \\frac{v}{R_{eq}} = \\frac{v}{R_1 + R_2 + \\dots + R_n}

The voltage drop across any individual resistor ($R_n$) is then:
v_n = i * R_n = \\frac{R_n}{R_{eq}} * v

> [!TIP]
> Use VDR to quickly find the voltage across any resistor in series without calculating the current first!"""
        ],
        example={
            'title': 'Worked Example: Series Loop Circuit',
            'description': 'Textbook Application: A single loop series circuit containing a 24V source and two resistors (8Ω and 4Ω) in series.',
            'circuit_def': {
                'topology': 'series',
                'components': [
                    {'type': 'V', 'name': 'V1', 'value': 24},
                    {'type': 'R', 'name': 'R1', 'value': 8},
                    {'type': 'R', 'name': 'R2', 'value': 4}
                ]
            },
            'solution_steps': [
                'Step 1: Assume a clockwise current i flowing around the loop.',
                'Step 2: Apply KVL starting from the voltage source negative terminal:',
                '        - The current enters the negative terminal of V1 first: -24V',
                '        - The current enters the positive terminal of R1: +v_1',
                '        - The current enters the positive terminal of R2: +v_2',
                '        KVL Loop Equation: -24 + v_1 + v_2 = 0',
                'Step 3: Express individual resistor voltages using Ohm\'s Law:',
                '        v_1 = 8 * i',
                '        v_2 = 4 * i',
                'Step 4: Substitute these into the KVL equation:',
                '        -24 + 8i + 4i = 0',
                '        12i = 24  =>  i = 2 A',
                'Step 5: Calculate the final voltage drop across each resistor:',
                '        v_1 = 8 * 2 = 16 V',
                '        v_2 = 4 * 2 = 8 V',
                'Step 6: Verification using the Voltage Divider Rule (VDR):',
                '        v_1 = (8 / (8 + 4)) * 24 = (8 / 12) * 24 = 16 V  (Matches perfectly!)'
            ]
        },
        problems=[
            {
                'description': 'KVL Practice 1: Series loop circuit',
                'question': 'Using KVL, determine the voltage drop across R1.',
                'circuit_def': {
                    'topology': 'series',
                    'components': [
                        {'type': 'V', 'name': 'V1', 'value': 24},
                        {'type': 'R', 'name': 'R1', 'value': 8},
                        {'type': 'R', 'name': 'R2', 'value': 4}
                    ]
                },
                'target_variable': 'V_R1',
                'unit': 'V',
                'hint': 'Apply KVL: -24 + V_R1 + V_R2 = 0. First find total current, then calculate V_R1 = I × R1.'
            },
            {
                'description': 'KVL Practice 2: Series voltage division',
                'question': 'Using KVL or voltage divider rule, determine the voltage drop across R2.',
                'circuit_def': {
                    'topology': 'series',
                    'components': [
                        {'type': 'V', 'name': 'V1', 'value': 30},
                        {'type': 'R', 'name': 'R1', 'value': 10},
                        {'type': 'R', 'name': 'R2', 'value': 5}
                    ]
                },
                'target_variable': 'V_R2',
                'unit': 'V',
                'hint': 'For a series circuit, the same current flows through all resistors. Use I = Vtotal / Rtotal, then V_R2 = I × R2.'
            }
        ],
    )

    module.add_lesson(lesson2)
    return module


def create_kcl_module():
    """Create Kirchhoff's Current Law learning module"""
    module = LearningModule(
        "Kirchhoff's Current Law (KCL)",
        "Learn how to apply KCL to analyze circuit nodes based on textbook fundamentals."
    )

    # Lesson 1: Circuit Elements & Power
    module.add_lesson(create_circuit_elements_lesson())

    # Lesson 2: Kirchhoff's Current Law
    lesson2 = Lesson(
        title="Kirchhoff's Current Law",
        theory_slides=[
            """# Kirchhoff's Current Law (KCL)

**Kirchhoff's Current Law (KCL)** is a fundamental circuit analysis law based on the **conservation of charge**. It states:
> The algebraic sum of all currents entering any node (or a closed boundary) is equal to zero.

### Mathematical Equation:
\\sum_{n=1}^{N} i_n = 0
where $N$ is the number of branches connected to the node and $i_n$ is the current flowing into or out of the node.

### The Golden Rule of KCL:
The sum of the currents entering a node is equal to the sum of the currents leaving it.
i_{entering} = i_{leaving}

> [!IMPORTANT]
> A node is a point in a circuit where two or more components connect. All points connected with zero-resistance wire form a single node.""",

            """# Understanding Nodes and Boundaries

KCL applies not only to a single point node but also to a **closed boundary** (supernode).

### Assigning Node Polarities:
When writing KCL equations, it is standard practice to:
1. Assign a direction (entering or leaving) to each branch current.
2. If the actual current direction is unknown, assume it flows **away** from the non-reference node (towards ground).
3. Sum all branch currents using Ohm's Law:
   i = \\frac{v_{start} - v_{end}}{R}

> [!TIP]
> The reference node (ground) is defined as having a potential of exactly 0V. We measure all other node voltages relative to this reference point.""",

            """# The Current Divider Rule (CDR)

When resistors are connected in **parallel**, the voltage across each component is identical, but the total entering current divides among the branches in inverse proportion to their resistances.

### The KCL-Derived Equations:
For two parallel resistors ($R_1$ and $R_2$) with an entering total current ($i_{total}$):
R_{eq} = \\frac{R_1 * R_2}{R_1 + R_2}

The branch currents are calculated as:
i_1 = \\frac{R_{eq}}{R_1} * i_{total} = \\frac{R_2}{R_1 + R_2} * i_{total}
i_2 = \\frac{R_{eq}}{R_2} * i_{total} = \\frac{R_1}{R_1 + R_2} * i_{total}

> [!NOTE]
> Notice that the current through $R_1$ depends on the value of $R_2$ in the numerator! More current always flows through the smaller resistance path."""
        ],
        example={
            'title': 'Worked Example: Parallel Node Circuit',
            'description': 'Textbook Application: A parallel circuit with a 12V voltage source and two parallel resistors (6Ω and 3Ω).',
            'circuit_def': {
                'topology': 'parallel',
                'components': [
                    {'type': 'V', 'name': 'V1', 'value': 12},
                    {'type': 'R', 'name': 'R1', 'value': 6},
                    {'type': 'R', 'name': 'R2', 'value': 3}
                ]
            },
            'solution_steps': [
                'Step 1: Identify the main node (top wire) and the reference node (bottom ground wire).',
                'Step 2: Because R1 and R2 are in parallel with the 12V source, the voltage across them is exactly V = 12V.',
                'Step 3: Calculate the branch currents using Ohm\'s Law:',
                '        i_1 = V / R1 = 12 / 6 = 2 A',
                '        i_2 = V / R2 = 12 / 3 = 4 A',
                'Step 4: Find the total current leaving the source using KCL:',
                '        i_total = i_1 + i_2 = 2 + 4 = 6 A',
                'Step 5: Verify using equivalent parallel resistance R_eq:',
                '        R_eq = (6 * 3) / (6 + 3) = 18 / 9 = 2 Ω',
                '        i_total = V / R_eq = 12 / 2 = 6 A  (Matches perfectly!)'
            ]
        },
        problems=[
            {
                'description': 'KCL Practice 1: Parallel branch currents',
                'question': 'Using KCL, determine the total current supplied by the source.',
                'circuit_def': {
                    'topology': 'parallel',
                    'components': [
                        {'type': 'V', 'name': 'V1', 'value': 12},
                        {'type': 'R', 'name': 'R1', 'value': 6},
                        {'type': 'R', 'name': 'R2', 'value': 3}
                    ]
                },
                'target_variable': 'I_total',
                'unit': 'A',
                'hint': 'Use Ohm’s Law to find each branch current. Then apply KCL: I_total = I_R1 + I_R2.'
            },
            {
                'description': 'KCL Practice 2: Current entering and leaving a node',
                'question': 'At a node, 5 A and 3 A enter, while 4 A leaves. Determine the unknown current leaving the node.',
                'answer': 4,
                'target_variable': 'I_unknown',
                'unit': 'A',
                'hint': 'Apply KCL: total current entering = total current leaving. Therefore, 5 + 3 = 4 + I_unknown.'
            }
        ],
    )

    module.add_lesson(lesson2)
    return module


def create_mesh_module():
    """Create Mesh Analysis module"""
    module = LearningModule(
        "Mesh Analysis",
        "Master the technique of analyzing complex circuits using mesh currents."
    )

    # Lesson 1: Circuit Elements & Power
    module.add_lesson(create_circuit_elements_lesson())

    # Lesson 2: Mesh Analysis
    lesson2 = Lesson(
        title="Mesh Analysis",
        theory_slides=[
            """# Mesh Analysis Fundamentals

**Mesh Analysis** is a powerful systematic technique for solving multi-loop circuits using **mesh currents** as the primary independent variables. 

### Core Concepts:
* **Loop:** Any closed path that starts and ends at the same node without passing through any node more than once.
* **Mesh:** A loop that **does not contain any other loops** within it.
* **Mesh Current:** An imaginary current assigned to flow around the perimeter of a particular mesh.

### Standard Step-by-Step Procedure:
1. Assign mesh currents ($i_1, i_2, \\dots, i_n$) to the meshes. It is standard to assume clockwise directions.
2. Apply KVL to each of the meshes. Use Ohm's Law to express the voltages in terms of the mesh currents.
3. Solve the resulting system of simultaneous equations to find the mesh currents.""",

            """# Shared Resistors and Current Sources

In multi-mesh circuits, elements may be shared between meshes, requiring special handling:

### 1. Handling Shared Resistors:
If resistor $R_3$ is shared between Mesh 1 ($i_1$) and Mesh 2 ($i_2$), the current through it depends on both:
* Looking from Mesh 1, the net clockwise current is $i_1 - i_2$. The voltage drop is $R_3 * (i_1 - i_2)$.
* Looking from Mesh 2, the net clockwise current is $i_2 - i_1$. The voltage drop is $R_3 * (i_2 - i_1)$.

### 2. Handling Current Sources (Case 1):
If a current source exists strictly on the outer branch of a mesh, that mesh current is immediately determined by the source value:
i_{mesh} = I_{source} (or -I_{source} if opposing directions)""",

            """# The Supermesh Concept (Case 2)

When a dependent or independent current source is **shared between two meshes**, we cannot write a standard KVL equation through the current source branch because the voltage across it is unknown. 

Instead, we create a **Supermesh**:

1. **Form the Supermesh:**
   Exclude the current source and any elements in series with it, forming a larger combined loop.
2. **Apply KVL:**
   Write a single KVL equation for the perimeter of the combined loop.
3. **Write the Constraint Equation:**
   Relate the two mesh currents directly to the shared current source:
   i_{leaving\\_direction} - i_{opposing\\_direction} = I_{source}

> [!IMPORTANT]
> A supermesh is a generalized loop that allows you to bypass the unknown voltage across current sources entirely!"""
        ],
        example={
            'title': 'Worked Example: Mesh Analysis',
            'description': 'Textbook Application: A two-loop circuit featuring a 15V source, a 5Ω resistor, a shared 10Ω resistor, a 10V source, a 6Ω resistor, and a 4Ω resistor.',
            'solution_steps': [
                'Step 1: Assign clockwise mesh currents i_1 to Mesh 1 and i_2 to Mesh 2.',
                'Step 2: Apply KVL to Mesh 1 (clockwise loop):',
                '        - The path goes through the 15V source, 5Ω resistor, shared 10Ω resistor, and 10V source.',
                '        Equation: -15 + 5*i_1 + 10*(i_1 - i_2) + 10 = 0',
                '        Simplify: 15*i_1 - 10*i_2 = 5  =>  3*i_1 - 2*i_2 = 1  (Eq. 1)',
                'Step 3: Apply KVL to Mesh 2 (clockwise loop):',
                '        - The path goes through the 10V source, shared 10Ω resistor, 6Ω resistor, and 4Ω resistor.',
                '        Equation: -10 + 10*(i_2 - i_1) + 6*i_2 + 4*i_2 = 0',
                '        Simplify: -10*i_1 + 20*i_2 = 10  =>  -i_1 + 2*i_2 = 1  (Eq. 2)',
                'Step 4: Solve the simultaneous equations (Eq. 1 and Eq. 2):',
                '        Add Eq. 1 and Eq. 2 together:',
                '        (3*i_1 - 2*i_2) + (-i_1 + 2*i_2) = 1 + 1',
                '        2*i_1 = 2  =>  i_1 = 1 A',
                '        Substitute i_1 into Eq. 2:',
                '        -1 + 2*i_2 = 1  =>  2*i_2 = 2  =>  i_2 = 1 A',
                'Step 5: Calculate the branch current through the shared 10Ω resistor:',
                '        i_shared = i_1 - i_2 = 1 - 1 = 0 A  (No net current flows through it!)'
            ]
        },
        problems=[],
        video_url="https://www.youtube.com/watch?v=WupqAtyE6tI"
    )
    module.add_lesson(lesson2)
    return module


def create_nodal_module():
    """Create Nodal Analysis module"""
    module = LearningModule(
        "Nodal Analysis",
        "Learn how to find node voltages using KCL based on the textbook method."
    )

    # Lesson 1: Circuit Elements & Power
    module.add_lesson(create_circuit_elements_lesson())

    # Lesson 2: Nodal Analysis
    lesson2 = Lesson(
        title="Nodal Analysis",
        theory_slides=[
            """# Nodal Analysis Fundamentals

**Nodal Analysis** is a highly structured procedure for solving circuits using **node voltages** as the primary independent variables. Measuring node voltages instead of branch voltages significantly reduces the number of simultaneous equations required.

### Core Concepts:
* **Reference Node (Ground):** The node selected as the common reference point. Its potential is defined as exactly 0V.
* **Node Voltage:** The voltage of a non-reference node measured with respect to ground.

### Standard Step-by-Step Procedure:
1. Select one reference node (ground). Assign voltages ($v_1, v_2, \\dots, v_{n-1}$) to the remaining $n-1$ non-reference nodes.
2. Apply KCL at each non-reference node. Express the branch currents in terms of the node voltages using Ohm's Law:
   i = \\frac{v_{higher} - v_{lower}}{R}
3. Solve the resulting system of simultaneous equations to find the unknown node voltages.""",

            """# Handling Voltage Sources

When a voltage source is present in the circuit, it defines the relationship between node voltages directly, leading to two distinct cases:

### Case 1: Voltage Source connected to Ground
If an independent or dependent voltage source ($V_s$) is connected between ground and a non-reference node ($v_1$), we simply set that node voltage equal to the source voltage:
v_1 = V_s
This removes node $v_1$ from our KCL equations, simplifying the solution process!

### Case 2: Voltage Source between two Non-Reference Nodes
If a voltage source is connected between two non-reference nodes ($v_1$ and $v_2$), the current through it is unknown. This requires the creation of a **Supernode**.""",

            """# The Supernode Concept

When a voltage source connects two non-reference nodes ($v_1$ and $v_2$), we enclose the voltage source and any parallel components in a generalized **Supernode** boundary.

### Two-Step Supernode Analysis:
1. **Apply KCL at the Supernode:**
   Treat the supernode as a single large node. Sum all currents entering and leaving this boundary:
   \\sum i_{entering} = \\sum i_{leaving}
   For example: \\frac{v_1 - v_{gnd}}{R_1} + \\frac{v_2 - v_{gnd}}{R_2} = I_{source}

2. **Write the Constraint Equation:**
   Establish the voltage relationship inside the supernode using KVL:
   v_{positive\\_terminal} - v_{negative\\_terminal} = V_s

> [!IMPORTANT]
> The supernode reduces the number of non-reference node equations by one, while providing a direct algebraic constraint equation!"""
        ],
        example={
            'title': 'Worked Example: Supernode Analysis',
            'description': 'Textbook Application: A circuit featuring two non-reference nodes. A 12V voltage source is connected between node 1 and node 2 (positive terminal at node 1). Resistors to ground are R1 = 4Ω (node 1) and R2 = 2Ω (node 2). A 6A current source enters node 1, and a 4A current source enters node 2.',
            'solution_steps': [
                'Step 1: Enclose the 12V voltage source in a supernode boundary between node 1 and node 2.',
                'Step 2: Apply KCL to the supernode (Sum of entering currents = Sum of leaving currents):',
                '        - Currents entering the supernode: 6A (into node 1) and 4A (into node 2).',
                '        - Currents leaving to ground: i_1 = v_1 / 4 (from node 1) and i_2 = v_2 / 2 (from node 2).',
                '        Equation: 6 + 4 = (v_1 / 4) + (v_2 / 2)',
                '        Multiply by 4 to clear fractions: 40 = v_1 + 2*v_2  (Eq. 1)',
                'Step 3: Write the voltage source constraint equation inside the supernode:',
                '        - The 12V source positive terminal is at node 1, negative at node 2.',
                '        Equation: v_1 - v_2 = 12  =>  v_1 = v_2 + 12  (Eq. 2)',
                'Step 4: Substitute Eq. 2 into Eq. 1:',
                '        40 = (v_2 + 12) + 2*v_2',
                '        40 = 3*v_2 + 12',
                '        28 = 3*v_2  =>  v_2 = -1.33 V  (or -4/3 V)',
                'Step 5: Solve for v_1:',
                '        v_1 = v_2 + 12 = -1.33 + 12 = 10.67 V  (or 32/3 V)',
                'Step 6: Verify the individual currents leaving the nodes:',
                '        i_1 = v_1 / 4 = 10.67 / 4 = 2.67 A',
                '        i_2 = v_2 / 2 = -1.33 / 2 = -0.67 A',
                '        Sum of leaving currents: i_1 + i_2 = 2.67 - 0.67 = 2.0 A',
                '        Net current source entering: 6A - 4A = 2A. Perfect KCL confirmation!'
            ]
        },
        problems=[],
        video_url="https://www.youtube.com/watch?v=S2u1A6Iq8nE"
    )
    module.add_lesson(lesson2)
    return module


def get_all_modules():
    """Return all available learning modules"""
    return {
        'kvl': create_kvl_module(),
        'kcl': create_kcl_module(),
        'mesh': create_mesh_module(),
        'nodal': create_nodal_module()
    }
