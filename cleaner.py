import pandas as pd
import re

# Function to clean the date format
def clean_date(date_str):
    # Extract the date part in the format "Month Day, Year"
    match = re.search(r'(\w+ \d{1,2}, \d{4})', date_str)
    if match:
        return match.group(1)
    return date_str  # Return the original if no match is found

# Load the CSV file
file_path = 'timesofindia.csv'  # Update this path to your file
df = pd.read_csv(file_path)

# Drop duplicate headlines
df.drop_duplicates(subset="Headline", inplace=True)

# Clean the date column
df['Date'] = df['Date'].apply(clean_date)

# Save the cleaned data to a new CSV
cleaned_file_path = 'timesofindia-modified.csv'
df.to_csv(cleaned_file_path, index=False)

print(f"Cleaned data saved to {cleaned_file_path}")
