"""Build 2017 REF_REGION Technologies from 2035 base, adding 2 extra coal cogen techs."""
import csv

# Load 2035 REF
with open('Data/2035/02_REF_REGION/Technologies.csv') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows_2035 = list(reader)

# Load 2017 REF to get the 2 extra coal cogen rows
with open('Data/2017/02_REF_REGION/Technologies.csv.bak_20260308_pre2035') as f:
    reader = csv.DictReader(f)
    rows_2017 = {row['Technologies param']: row for row in reader}

print(f"2035 REF: {len(rows_2035)} rows")
print(f"Fieldnames: {fieldnames}")

# Get the 2 coal cogen from 2017
extra_techs = ['IND_COGEN_COAL', 'DHN_COGEN_COAL']
for name in extra_techs:
    if name in rows_2017:
        r = rows_2017[name]
        print(f"\n{name}:")
        for col, val in r.items():
            print(f"  {col}: {val}")

# Build output: 2035 rows + 2 extra coal cogen rows from 2017
# Insert them in appropriate positions (after their non-coal siblings)
output_rows = list(rows_2035)  # start with all 2035

for name in extra_techs:
    if name in rows_2017:
        output_rows.append(rows_2017[name])

print(f"\nOutput: {len(output_rows)} rows")

# Write the new 2017 REF_REGION Technologies
with open('Data/2017/02_REF_REGION/Technologies.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in output_rows:
        writer.writerow(row)

print("Written to Data/2017/02_REF_REGION/Technologies.csv")
