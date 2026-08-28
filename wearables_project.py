import pandas as pd
import matplotlib.pyplot as plt
import os

# Location of the wearable data file
file_path = "path/to/wearables_all_labelled.xlsx"

#Loads the Excel file into pandas
df = pd.read_excel(file_path)


# Basic information on the dataset
print(df.head())
print(df.columns)
print(df.shape)
print(df.info())

df["dateTime"] = pd.to_datetime(
    df["dateTime"],
    errors="coerce"
)


# Find each participant's average steps
participant_steps = (
    df.groupby("alias")["steps"]
      .agg(["mean", "count"])
      .sort_values("mean")
)


print(participant_steps)

# Creates a bar graph displaying the average steps per particapant 
participant_steps["mean"].plot(
    kind="barh",
    figsize=(10, 6),
    title="Average Steps by Participant"
)


plt.xlabel("Average steps")
plt.ylabel("Participant alias")
plt.tight_layout()
plt.show()


#Split date and time into different date and time columns 
df["date"] = df["dateTime"].dt.date
df["time"] = df["dateTime"].dt.time

#Prints the intial rows to check if the split works
print(df[["dateTime", "date", "time"]].head())

# Show how many particpants there are 
print("Number of aliases:", df["alias"].nunique())

# Show how many rows of data each participant has 
print(df["alias"].value_counts())

# Make the main Output folder
output_folder = "Output"
os.makedirs(output_folder, exist_ok=True)

# Go through each participant
for alias, alias_data in df.groupby("alias"):

    # Make a folder for that participant
    alias_folder = os.path.join(output_folder, str(alias))
    os.makedirs(alias_folder, exist_ok=True)

    # Split that participant's data by date
    for date, daily_data in alias_data.groupby("date"):

        # Save each day as its own CSV
        daily_file_path = os.path.join(alias_folder, f"{date}.csv")
        daily_data.to_csv(daily_file_path, index=False)

print("done")


# Check how many values are missing in each column
print("Missing values:")
print(df.isna().sum())


# Show the data type of each column
print("\nData types:")
print(df.dtypes)


# check for duplicate rows
print("\nDuplicate rows:")
print(df.duplicated().sum())


#Check numeric columns for negative values
print("\nNegative values in numeric columns:")
numeric_cols = df.select_dtypes(include="number").columns

for col in numeric_cols:
    negative_count = (df[col] < 0).sum()

    if negative_count > 0:
        print(col, negative_count)


# Save a statistical summary of the dataset
summary = df.describe(include="all")
summary.to_csv("statistical_summary.csv")


# Save a summary of some data quality issues
quality_summary = pd.DataFrame({
    "missing_values": df.isna().sum(),
    "data_type": df.dtypes,
    "negative_values": [
        (df[col] < 0).sum()
        if pd.api.types.is_numeric_dtype(df[col])
        else 0
        for col in df.columns
    ]
})

quality_summary.to_csv("data_quality_summary.csv")

