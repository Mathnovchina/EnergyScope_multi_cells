
import sys
import pandas as pd
from pathlib import Path
import logging

# Add project root to sys.path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.append(str(workspace_root))

from esmc import Esmc

def check_violated_constraints():
    config = {
        'case_study': 'calib_2017_finland_v9',
        'comment': 'Debug Constraints',
        'regions_names': ['FI'],
        'gwp_limit_overall': None, 
        'f_perc': True, 
        'year': 2017,
        're_share_primary': None
    }
    
    print("Initializing ESMC model...")
    my_model = Esmc(config, nbr_td=12)
    my_model.read_data_indep()
    my_model.init_regions()
    my_model.init_ta(algo='kmedoid') 
    
    print("Setting up AMPL...")
    my_model.set_esom(solver='cplex') 
    ampl = my_model.esom.ampl
    
    # Increase tolerance just to see if it solves 'cleanly' with loose tolerance?
    # ampl.setOption('cplex_options', 'feasibility=1e-4 optimality=1e-4')
    
    print("Solving...")
    try:
        ampl.solve()
    except Exception as e:
        print(f"Solve raised exception: {e}")

    solve_result = ampl.getValue("solve_result")
    print(f"Solve Result: {solve_result}")
    
    print("Checking for violated constraints...")
    # By checking slack variables
    # For EQ constraints: body = lb = ub. Violation if abs(body - lb) > tol.
    # For LEQ/GEQ: body <= ub. Violation if body > ub + tol.
    
    # We can ask AMPL to display violated constraints
    # But doing it programmatically is better.
    
    # Let's iterate over all objectives first to see what drives the cost
    obj_val = ampl.getObjective("obj").value()
    print(f"Total Objective: {obj_val}")
    
    # AMPL has a way to list violated constraints
    # 'display {j in 1.._ncons: _con[j].slack < -1e-5} (_conname[j], _con[j].slack);'
    
    print("\n--- VIOLATED CONSTRAINTS (Slack < -1e-3) ---")
    try:
        # Check lower bound violations (body < lb) -> slack = body - lb < 0? 
        # Actually in AMPL:
        # lslack = body - lb (should be >= 0)
        # uslack = ub - body (should be >= 0)
        # slack = min(lslack, uslack) ?
        # It's better to check violations directly.
        # _con[j] is the current value of the constraint body? No, it's the dual?
        # ampl.eval('display {j in 1.._ncons: _con[j].slack < -1e-3} (_conname[j], _con[j].slack);')
        
        # Let's try to export them to a dataframe
        cmd = """
        for {j in 1.._ncons} {
            if abs(_con[j].lslack) < -1e-3 or abs(_con[j].uslack) < -1e-3 then {
                print _conname[j], _con[j].lslack, _con[j].uslack;
            }
        }
        """
        # Better:
        # display _conname, _con.body, _con.lb, _con.ub
        # Filter where mismatch
        
        # Using AMPL's built-in violation checker if available?
        # Or just manually inspect expected big contributors
    except:
        pass

    # Let's look at `TotalCost` components
    print("\n--- Cost Breakdown ---")
    try:
        ampl.eval("display sum {c in REGIONS} C_inv[c];")
        ampl.eval("display sum {c in REGIONS} C_maint[c];")
        ampl.eval("display sum {c in REGIONS} C_op[c];")
        # Ensure we check penalty costs if they exist directly
    except:
        pass

    # Let's check huge variables
    print("\n--- Suspiciously Large Variables (> 1e12) ---")
    # This loop might be slow if many vars, but we need to find what's exploding
    # Maybe checking 'F_t' or 'Capacity'
    # ampl.eval("display {j in 1.._nvars: _var[j] > 1e15} (_varname[j], _var[j]);")

    # Use Python to iterate constraints more safely
    for con in ampl.getConstraints():
        c = con[1]
        try:
             # This gets the constraint entity. We need to iterate its instances.
             # If it's indexed...
             # This is slow.
             pass
        except:
            pass

    # Let's run a specific AMPL command to find the culprit
    # Violation is body - bnd
    # Define a parameter for violation?
    print("Finding max violations...")
    ampl.eval('param max_viol default 0;')
    ampl.eval('let max_viol := 0;')
    ampl.eval('display solve_message;')
    
    # Check "Tolerance violations" reported in log
    # They are likely from:
    # layer_balance
    # storage_level
    
    # Focus on layer_balance
    # print all layer_balance with slack
    # ampl.eval('display {c in REGIONS, l in LAYERS, h in HOURS, td in TYPICAL_DAYS: layer_balance[c,l,h,td].slack < -1000} (c,l,h,td, layer_balance[c,l,h,td].slack);')
    # Too many indices.
    
    # Check if 'TotalCost' is part of an equation that is violated?
    # No, TotalCost is a variable in the objective.
    
    # If the objective is 5e17, checking the objective components is key.
    # The objective is 'minimize obj: sum{c in REGIONS} TotalCost[c];'
    # Check TotalCost variable.
    print("Breakdown of TotalCost:")
    ampl.eval('display {c in REGIONS} TotalCost[c];')
    
    # Check C_inv, C_maint, C_op
    ampl.eval('display {c in REGIONS} C_inv[c];')
    ampl.eval('display {c in REGIONS} C_maint[c];')
    ampl.eval('display {c in REGIONS} C_op[c];')

if __name__ == "__main__":
    check_violated_constraints()
