import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parents[1]
sys.path.append(str(project_root))

from esmc.postprocessing.draw_sankey.output_to_sankey_csv import write_sankey_file
from esmc.postprocessing.draw_sankey.ESSankey import drawSankey

def main():
    space_id = "FI"
    case_study = "ref_2017_finland"
    
    print(f"Generating Sankey CSVs for {space_id}/{case_study}...")
    try:
        write_sankey_file(space_id, case_study)
        print("CSV generation done.")
    except Exception as e:
        print(f"Error in CSV generation: {e}")
        # Proceeding might fail if CSVs are missing
    
    # Define output path
    output_dir = project_root / "case_studies" / space_id / case_study / "outputs"
    
    print(f"Generating Sankey HTML in {output_dir}...")
    try:
        # drawSankey expects 'path' to contain input2sankey files.
        drawSankey(path=output_dir, outputfile='python_generated_sankey.html', I2S_File="input2sankey_Total.csv", auto_open=False)
        print(f"Sankey generated successfully.")
    except Exception as e:
        print(f"Error in HTML generation: {e}")

if __name__ == "__main__":
    main()
