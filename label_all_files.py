import pandas as pd
import os

# Location of the wearable data file
file_path = "path/to/wearables_all_labelled.xlsx"
df = pd.read_excel(file_path)

# Convert timestamp columns to date/time
df["dateTime"] = pd.to_datetime(df["dateTime"], errors="coerce")
df["scoreDate"] = pd.to_datetime(df["scoreDate"], errors="coerce")

# New folder for the fully labelled files
output_folder = "Output_Labeled"

os.makedirs(output_folder, exist_ok=True)

# Go through one participant at a time
for alias, person in df.groupby("alias"):

    person = person.copy()

    # Get the score dates and scores for this participant
    labels = (
        person[["scoreDate", "score"]]
        .dropna()
        .drop_duplicates()
        .sort_values("scoreDate")
    )

    # Creates a date-only versions for matching
    person["sensorDate"] = person["dateTime"].dt.normalize()

    # Remove old score columns before adding the labels
    person = person.drop(
        columns=["score", "scoreDate"],
        errors="ignore"
    )

    if len(labels) > 0:

        labels["scoreDay"] = labels["scoreDate"].dt.normalize()

        # Match each sensor date with the next future score date
        labelled = pd.merge_asof(
            person.sort_values("sensorDate"),
            labels.sort_values("scoreDay"),
            left_on="sensorDate",
            right_on="scoreDay",
            direction="forward"
        )

        # Calculate how many days apart they are using subtraction
        labelled["DaysElapsed"] = (
            labelled["scoreDay"] - labelled["sensorDate"]
        ).dt.days

    else:

        # In case a participant has no score information
        labelled = person.copy()
        labelled["scoreDate"] = pd.NaT
        labelled["score"] = pd.NA
        labelled["scoreDay"] = pd.NaT
        labelled["DaysElapsed"] = pd.NA

    # Put sensor rows back into chronological order
    labelled = labelled.sort_values("dateTime")

    # Separate date and time
    labelled["date"] = labelled["dateTime"].dt.date
    labelled["time"] = labelled["dateTime"].dt.time

    # Remove temporary columns used only for matching
    labelled = labelled.drop(
        columns=["sensorDate", "scoreDay"],
        errors="ignore"
    )

    # Create a folder for this participant
    alias_folder = os.path.join(
        output_folder,
        str(alias)
    )

    os.makedirs(alias_folder, exist_ok=True)

    # Create one CSV for each date
    for date, daily_data in labelled.groupby("date"):

        save_path = os.path.join(
            alias_folder,
            f"{date}.csv"
        )

        daily_data.to_csv(
            save_path,
            index=False
        )

    print("Finished:", alias)
