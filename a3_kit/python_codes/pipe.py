import csv

with open(r'D:\prudhvi\Dev\temp_storage\page0.csv', 'r') as fin, \
    open(r'D:\prudhvi\Dev\temp_storage\page0.txt', 'w') as fout:
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, reader.fieldnames, delimiter='|')
    writer.writeheader()
    writer.writerows(reader)
