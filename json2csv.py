import json
import csv

results_data = open('ICE.txt')
barchart_parsed = json.load(results_data)
barchart_data = barchart_parsed['results']

# open a file for writing

bar_data = open('/ICEData.csv', 'w')

# create the csv writer object

csvwriter = csv.writer(bar_data)
count = 0

for day in barchart_data:
      if count == 0:
             header = day.keys()
             csvwriter.writerow(header)
             count += 1
      csvwriter.writerow(day.values())
bar_data.close()
