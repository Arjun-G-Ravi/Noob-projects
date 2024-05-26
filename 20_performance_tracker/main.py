import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date, datetime
import helper
from PIL import Image


db_location = '/home/arjun/Desktop/Datasets/plan.csv'
work = ['AI Theory', 'AI Project', 'Programming', 'Non-AI', 'Workout', 'Total']

if os.path.exists(db_location):
    db = pd.read_csv(db_location)
    print('Read from existing database')
else:
    data = {
    'Date': [], 'AI Theory': [], 'AI Project': [],
    'Programming': [], # Leetcode + Non AI project
    'Non-AI': [], # Non AI, Non programming
    'Workout': [],  'Total': []}

    db = pd.DataFrame(data)
    db.to_csv(db_location, index=False)
    print('Created empty database')

ct = 0
new_data = {}

try:
    for k in work + ['Date']:
        if k == 'Date':
            new_data[k] = f'{date.today().day}-{date.today().month}-{date.today().year}'
            print(new_data)
        elif k == 'Total':
            new_data[k] = ct
        else:
            val = float(input(f'Time spend in {k}:'))
            if k == 'Workout':
                if val: val=1 # Workout is True/ False
            new_data[k] = val
            ct += val
    
    db = helper.add_row(db, new_data)
    db.to_csv(db_location, index=False)
except:
    print('Did not create new row.')


d = {k:sum(v) for k,v in db.items() if k!='Date'}
df = pd.DataFrame({'Work': d.keys(), 'Time': d.values()})

work = ['AI Theory', 'AI Project', 'Programming', 'Non-AI', 'Workout', 'Total']
time_total = [800, 1100, 370, 730, 300, 3000]
df_total = pd.DataFrame({'Work': work, 'Time': time_total})
year_progress = (370 - (datetime(2025, 6, 1) - datetime.today()).days)/370*100 
time_year = [t*year_progress for t in time_total]
df_year = pd.DataFrame({'Work': work, 'Time': time_year})

fig, ax = plt.subplots(figsize=(20, 8))

df.plot(kind='barh', x='Work', y='Time', legend=False, alpha=1, ax=ax)
df_total.plot(kind='barh', x='Work', y='Time', legend=False, alpha=0.3, ax=ax)
df_year.plot(kind='barh', x='Work', y='Time', legend=False, alpha=0.2, ax=ax)

for index, value in enumerate(df['Time']):
    ax.text(value, index, str(round(value*100/df_total['Time'][index],2)) + ' %', color='black', va='center', ha='left', fontsize=12)

plt.title(f'Year Progress: {year_progress*100} %')
plt.ylabel('Work')
plt.xlabel('Time')
image_path = './20_performance_tracker/year_progress_plot.png'
plt.savefig(image_path)

img = Image.open(image_path)
img.show()