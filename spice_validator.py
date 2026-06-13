import logging
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import u_V, u_Ohm, u_A

class SpiceValidator:
    def __init__(self):
        # Disable PySpice logging to console
        logging.getLogger('PySpice').setLevel(logging.WARNING)
        
        # Set path to NGSPICE DLL
        import os
        import platform
        from PySpice.Spice.NgSpice.Shared import NgSpiceShared
        
        # Common installation path for Spice64
        dll_path = r"C:\Spice64_dll\dll-vs\ngspice.dll"
        if os.path.exists(dll_path):
             print(f"DEBUG: Found NGSPICE at {dll_path}")
             NgSpiceShared.LIBRARY_PATH = dll_path
             
             # Add to PATH to ensure dependencies are found (fixes error 0x7e)
             bin_dir = os.path.dirname(dll_path)
             os.environ["PATH"] += os.pathsep + bin_dir
        else:
             print(f"DEBUG: NGSPICE not found at {dll_path}")

    def validate_circuit(self, circuit_def):
        """
        Validates the circuit using PySpice/NGSPICE.
        Returns a dictionary of simulated values.
        """
        try:
            circuit = self._build_circuit(circuit_def)
            simulator = circuit.simulator(temperature=25, nominal_temperature=25)
            analysis = simulator.operating_point()
            
            results = {}
            
            # 1. Extraction for Node-based entries (Visual Builder)
            if all('nodes' in c for c in circuit_def.get('components', [])):
                # Extract branch currents
                for branch_name, current in analysis.branches.items():
                    name = branch_name.upper()
                    results[f'I_{name}'] = float(current)
                
                # Extract node voltages
                for node_name, voltage in analysis.nodes.items():
                    results[f'V_node_{node_name}'] = float(voltage)
                
                # Calculate component voltages: V_comp = V_n1 - V_n2
                # We need to find node IDs again. 
                # Let's map sn1, sn2 logic from _build_circuit
                v1_n2 = 1
                for c in circuit_def['components']:
                    if c['type'] == 'V': v1_n2 = c['nodes'][1]; break
                
                for c in circuit_def['components']:
                    n1, n2 = c['nodes']
                    sn1 = '0' if n1 == v1_n2 else str(n1)
                    sn2 = '0' if n2 == v1_n2 else str(n2)
                    
                    v_n1 = float(analysis.nodes.get(sn1, 0))
                    v_n2 = float(analysis.nodes.get(sn2, 0))
                    results[f'V_{c["name"]}'] = abs(v_n1 - v_n2)
                
                # Total current is from V1
                if 'i_v1' in results: results['I_total'] = abs(results['i_v1'])
                elif 'I_V1' in results: results['I_total'] = abs(results['I_V1'])

            # 2. Extraction for Topology-based entries (Problem Bank)
            elif circuit_def['topology'] == 'series':
                for node in analysis.nodes.values():
                    results[f'V_node_{str(node)}'] = float(node)
                
                if 'v1' in analysis.branches:
                    results['I_total'] = float(-analysis.branches['v1'])
                elif 'V1' in analysis.branches:
                    results['I_total'] = float(-analysis.branches['V1'])
                    
            return results
            
        except Exception as e:
            return {'error': str(e)}

    def _build_circuit(self, circuit_def):
        circuit = Circuit('Virtual Tutor Circuit')
        components = circuit_def.get('components', [])
        
        # 1. Use manual Node IDs if available (Visual Builder mode)
        has_nodes = all('nodes' in c for c in components)
        
        if has_nodes:
            # Shift nodes so that 1 becomes circuit.gnd if 0 isn't present
            # Or just use node 0 if it exists. PySpice uses 0 for GND.
            for c in components:
                n1, n2 = c['nodes']
                # PySpice uses 0 for GND. Our extractor starts at 1. 
                # Let's map Node 1 to GND (0) or check if V source negative is GND
                # For simplicity, if V1 exists, its node 0 terminal should be GND.
                # Actually, our extractor just numbers them. 
                # Let's just use the numbers. If someone connect to node 1, it's node 1.
                # BUT we MUST have a node 0 (GND).
                v1_n2 = 1 # fallback
                for comp in components:
                    if comp['type'] == 'V':
                        v1_n2 = comp['nodes'][1] # Negative terminal node
                        break
                
                # Map nodes so that v1_n2 becomes 0 (GND)
                sn1 = 0 if n1 == v1_n2 else n1
                sn2 = 0 if n2 == v1_n2 else n2
                
                val = c['value']
                if c['type'] == 'V':
                    circuit.V(c['name'], sn1, sn2, val@u_V)
                elif c['type'] == 'R':
                    circuit.R(c['name'], sn1, sn2, val@u_Ohm)
            return circuit

        # 2. Fallback for Topology-based definitions (Problem Bank mode)
        if circuit_def['topology'] == 'series':
            v_source = next((c for c in components if c['type'] == 'V'), None)
            resistors = [c for c in components if c['type'] == 'R']
            if not v_source: raise ValueError("No voltage source found")
            
            # Series loop: GND -> V1 -> Node 1 -> R1 -> Node 2 -> ... -> GND
            circuit.V(v_source['name'], 1, circuit.gnd, v_source['value']@u_V)
            prev = 1
            for i, r in enumerate(resistors):
                curr = circuit.gnd if i == len(resistors) - 1 else i + 2
                circuit.R(r['name'], prev, curr, r['value']@u_Ohm)
                prev = curr
                
        elif circuit_def['topology'] == 'parallel':
            v_source = next((c for c in components if c['type'] == 'V'), None)
            resistors = [c for c in components if c['type'] == 'R']
            if not v_source: raise ValueError("No voltage source found")
            
            # Parallel: all across Node 1 and GND
            circuit.V(v_source['name'], 1, circuit.gnd, v_source['value']@u_V)
            for r in resistors:
                circuit.R(r['name'], 1, circuit.gnd, r['value']@u_Ohm)
                
        return circuit
