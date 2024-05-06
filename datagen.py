import pandas as pd
import numpy as np

# Define constants
SUBJECTS = ['Math', 'Science', 'English', 'History', 'Hindi', 'Marathi']
NUM_STUDENTS = 30
NUM_GRADES = 5
MIN_MARKS = 30
MAX_MARKS = 100

# Set seed for reproducibility
np.random.seed(42)

# Generate data
data = {'StudentID': [], 'Grade': [], 'Subject': [], 'Marks': []}
for student_id in range(1, NUM_STUDENTS + 1):
    for grade in range(1, NUM_GRADES + 1):
        for subject in SUBJECTS:
            marks = np.random.randint(MIN_MARKS, MAX_MARKS + 1)
            data['StudentID'].append(student_id)
            data['Grade'].append(grade)
            data['Subject'].append(subject)
            data['Marks'].append(marks)

# Create DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv('student_data.csv', index=False)
print("Data generated and saved to 'student_data.csv'")