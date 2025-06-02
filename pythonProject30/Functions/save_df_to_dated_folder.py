import os
from datetime import date


def save_df_to_dated_folder(df, days):
    today = date.today().isoformat()

    # Create parent folder with today's date
    parent_folder = f"Videos_{today}"
    os.makedirs(parent_folder, exist_ok=True)

    # Create subfolder for the given number of days inside the parent folder
    subfolder = os.path.join(parent_folder, f"last_{days}_days")
    os.makedirs(subfolder, exist_ok=True)

    # Save the DataFrame to a CSV file in the subfolder
    filename = f"{subfolder}/most_viewed_last_{days}_days_{today}.csv"
    df.to_csv(filename, index=False)

    print(f" Saved CSV to {filename}")
    return filename
