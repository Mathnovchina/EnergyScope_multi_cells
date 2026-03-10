import csv
rows = []
with open('Data/2017/FI/Technologies.csv','r',encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Technologies param'].strip() == 'PV_UTILITY':
            row['f_max'] = '0.1'
        if row['Technologies param'].strip() == 'PV_ROOFTOP':
            row['f_max'] = '0.3'
        rows.append(row)
with open('Data/2017/FI/Technologies.csv','w',encoding='utf-8-sig',newline='') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
