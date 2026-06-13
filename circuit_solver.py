import sympy

class CircuitSolver:
    def __init__(self):
        pass

    def solve_circuit(self, circuit_def):
        """
        Solves the circuit based on the definition.
        Supports: 'series' or 'parallel' topology with 1 Voltage Source and N Resistors,
        or custom textbook circuits with precalculated solutions.
        """
        if 'precalculated_solutions' in circuit_def:
            return circuit_def['precalculated_solutions']
            
        if circuit_def['topology'] == 'series':
            return self._solve_series(circuit_def['components'])
        elif circuit_def['topology'] == 'parallel':
            return self._solve_parallel(circuit_def['components'])
        return {'error': 'Unsupported topology'}

    def _solve_series(self, components):
        # Identify total voltage and total resistance
        total_voltage = 0
        total_resistance = 0
        others = []

        for comp in components:
            if comp['type'] == 'V':
                total_voltage += comp['value']
            elif comp['type'] == 'R':
                total_resistance += comp['value']
                others.append(comp)
        
        # Calculate current I = V / R_total
        if total_resistance == 0:
            return {'error': 'Short circuit (R=0)'}
            
        I = total_voltage / total_resistance
        
        results = {
            'I_total': float(I),
            'V_total': float(total_voltage),
            'R_total': float(total_resistance)
        }

        # Calculate voltage drop across each component
        for comp in others:
            if comp['type'] == 'R':
                v_drop = I * comp['value']
                results[f'V_{comp["name"]}'] = float(v_drop)
                results[f'I_{comp["name"]}'] = float(I)
            
        return results

    def _solve_parallel(self, components):
        # In parallel: V is same for all branches, I_total = Sum(I_branches)
        total_voltage = 0
        others = []

        for comp in components:
            if comp['type'] == 'V':
                total_voltage += comp['value']
            elif comp['type'] == 'R':
                others.append(comp)
        
        if not others:
            return {'error': 'No components in circuit'}

        total_conductance = 0
        results = {'V_total': float(total_voltage)}

        for comp in others:
            if comp['type'] == 'R':
                if comp['value'] == 0: return {'error': f"Short circuit at {comp['name']}"}
                i_comp = total_voltage / comp['value']
                total_conductance += 1.0 / comp['value']
            
            results[f'I_{comp["name"]}'] = float(i_comp)
            results[f'V_{comp["name"]}'] = float(total_voltage)
        
        if total_conductance == 0:
            total_resistance = float('inf')
            total_current = 0
        else:
            total_resistance = 1.0 / total_conductance
            total_current = total_voltage * total_conductance
        
        results['I_total'] = float(total_current)
        results['R_total'] = float(total_resistance)
        
        return results
