import os
import pandas as pd
from datetime import datetime
import subprocess

csv_file = '/Users/YOUR_NAME/Desktop/photos_metadata.csv'
df = pd.read_csv(csv_file)

photo_directory = "/Users/YOUR_NAME/Downloads/"

def convert_date(week, day, time_str):
    date_str = f"{week} {day} {time_str}"
    return datetime.strptime(date_str, "%A %B %d %Y at %I:%M:%S %p")

for index, row in df.iterrows():
    filename = row['Filename']
    creation_date_iso = row['CreationDate']
    
    try:
        creation_date = datetime.fromisoformat(creation_date_iso.replace('Z', '+00:00')).strftime('%Y:%m:%d %H:%M:%S')

        
        file_path = os.path.join(photo_directory, filename)
        
        if os.path.exists(file_path):
            # exiftool
            subprocess.run([
                'exiftool',
                f'-Alldates={creation_date}',
                f'-FileModifyDate={creation_date}',
                '-overwrite_original',
                file_path
            ], check=True)
            print(f"Updated {file_path} to {creation_date}")
        else:
            print(f"File {file_path} does not exist")
    except Exception as e:
        print(f"Could not process file {filename}: {e}")
