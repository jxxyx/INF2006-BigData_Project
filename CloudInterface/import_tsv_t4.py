import pandas as pd
import os
import django
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CloudInterface.settings')
django.setup()

from myapp.models import Task4, UserProfile

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
    # Load the TSV file
    data = pd.read_csv(file_path, sep='\t', quoting=3, skipinitialspace=True)
except Exception as e:
    print(f"Error reading the file: {e}")
    exit()

# Print a preview of the file for user confirmation
print("\nPreview of the data:")
print(data.head())

# Confirm with the user before importing data
confirm = input("\nDo you want to proceed with uploading this data to the database? (yes/no): ").strip().lower()
if confirm != "yes":
    print("Operation canceled.")
    exit()

# Loop through each row in the DataFrame and save it to the database
for _, row in data.iterrows():
    try:
        # Ensure a default user exists or create one
        user, created = UserProfile.objects.get_or_create(username='default_user', password='password123')
        
        # Create Task4 instance
        Task4.objects.create(
            Channel=row['Channel'],
            Mean_Trust_Score=row['Mean_Trust_Score'],
            Median_Trust_Score=row['Median_Trust_Score'],
            Standard_Deviation=row['Standard_Deviation'],
            Sample_Size=row['Sample_Size'],
            Min_Score=row['Min_Score'],
            Max_Score=row['Max_Score'],
            user=user
        )
    except Exception as e:
        print(f"Error uploading row: {e}")
        continue

print("Data uploaded successfully!")
