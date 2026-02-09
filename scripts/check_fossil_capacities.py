import pandas as pd
from pathlib import Path

# Config
BASE_DIR = Path(r"c:/Users/borde/OneDrive/Bureau/model/EnergyScope_multi_cells")
EXCEL_PATH = BASE_DIR / "Data/exogenous_data/Finland_MASTER_Calibration.xlsx"

def get_fossil_capacities():
    print("Reading Excel Technologies...")
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="4_Technologies", skiprows=0)
        print("Columns:", df.columns.tolist())
        print("First 10 rows of 'Technologies param':")
        print(df['Technologies param'].head(10))
        
        # Filter for relevant fossil keywords
        keywords = ['COAL', 'GAS', 'OIL', 'PEAT', 'CCGT']
        
        # Ensure string matching works
        df['Technologies param'] = df['Technologies param'].astype(str)
        
        # Print all techs to see what's there
        print("All Technologies:")
        for t in df['Technologies param'].unique():
             print(t)
        
        mask = df['Technologies param'].apply(lambda x: any(k in x.upper() for k in keywords))
        fossil_df = df[mask][['Technologies param', 'f_min', 'f_max']]
        
        print(fossil_df)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_fossil_capacities()
