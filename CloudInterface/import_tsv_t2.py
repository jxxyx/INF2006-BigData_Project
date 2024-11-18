import pandas as pd
import os
import django
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CloudInterface.settings')
django.setup()

from myapp.models import Task2, UserProfile

# Use tkinter to open a file dialog
def select_file():
    Tk().withdraw()  # Hides the main Tkinter window
    file_path = askopenfilename(
        title="Select the TSV file",
        filetypes=[("TSV files", "*.tsv"), ("All files", "*.*")]
    )
    return file_path

# Prompt the user to select the file
print("Please select the TSV file from your file explorer.")
file_path = select_file()

# Check if the user selected a file
if not file_path:
    print("No file selected. Exiting.")
    exit()

# Load the TSV file into a pandas DataFrame
try:
    # Remove quotes and correctly parse the data
    data = pd.read_csv(file_path, sep='\t', quoting=3, skipinitialspace=True)
    # Remove surrounding quotes from column headers and values
    data.columns = data.columns.str.replace('"', '').str.strip()
    data = data.applymap(lambda x: x.replace('"', '').strip() if isinstance(x, str) else x)
except Exception as e:
    print(f"Error reading the file: {e}")
    exit()

# Print a preview of the file for user confirmation
print("\nPreview of the data:")
print(data.head())

# Allow the user to filter by column if desired
filter_column = input("\nEnter the column you want to filter by (or press Enter to skip): ").strip()
filter_value = None

if filter_column:
    if filter_column not in data.columns:
        print(f"Column '{filter_column}' not found in the file.")
        exit()

    filter_value = input(f"Enter the value you want to filter '{filter_column}' by: ").strip()
    # Filter the DataFrame
    data = data[data[filter_column] == filter_value]

# Confirm with the user before importing data
print("\nFiltered data (if any):")
print(data)

confirm = input("\nDo you want to proceed with uploading this data to the database? (yes/no): ").strip().lower()
if confirm != "yes":
    print("Operation canceled.")
    exit()

# Loop through each row in the DataFrame and save it to the database
for _, row in data.iterrows():
    user, created = UserProfile.objects.get_or_create(username='default_user', password='password123')
    Task2.objects.create(
        Airline=row['Airline'],
        Reason=row['Reason'],
        Count=row['Count'],
        user=user
    )

print("Data uploaded successfully!")