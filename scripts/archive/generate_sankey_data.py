import sys
import os
from pathlib import Path

# Add the project root to sys.path so we can import esmc
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from esmc.postprocessing.draw_sankey.output_to_sankey_csv import write_sankey_file

def main():
    space_id = "FI"
    case_study = "ref_2017_finland"
    
    print(f"Generating Sankey CSVs for {space_id}/{case_study}...")
    try:
        write_sankey_file(space_id, case_study)
        print("Sankey CSVs generated successfully.")
    except Exception as e:
        print(f"Error generating Sankey CSVs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
