import pandas as pd
import json
import re
from src.projections import calculate_cumulative_projections
from src.parser import parse_date_and_names, append_to_csv

def update_json(csv_path, json_path):
    """
    Reads data from a CSV file and updates a JSON file accordingly.
    """
    df = pd.read_csv(csv_path)
    df["Date"] = df["Date"].astype(str)

    # Calculate cumulative differences
    cumulative_df = df.copy()
    cumulative_df.iloc[:, 1:] = df.iloc[:, 1:].cumsum(axis=0)

    # Extend dates for projections
    num_projection_days = 5
    last_date_parts = df["Date"].iloc[-1].split(".")
    last_month, last_day = int(last_date_parts[0]), int(last_date_parts[1])
    future_dates = []
    for i in range(1, num_projection_days + 1):
        last_day += 1
        if last_day > 31:
            last_day = 1
            last_month += 1
        if last_month > 12:
            last_month = 1
        future_dates.append(f"{last_month:02d}.{last_day:02d}")

    extended_dates = df["Date"].tolist() + future_dates

    # Add projections
    projections = {}
    for col in df.columns[1:]:
        values = df[col].values.tolist()
        last_cumulative = cumulative_df[col].values[-1]
        # projections[col] = calculate_cumulative_projections(values, last_cumulative)
        projections[col] = calculate_cumulative_projections(values, last_cumulative, num_forecasts=5)

    # Combine data for saving
    combined_data = {
        "dates": extended_dates,
        "raw_values": df.iloc[:, 1:].to_dict(orient="list"),
        "cumulative_values": cumulative_df.iloc[:, 1:].to_dict(orient="list"),
        "projections": projections,
    }

    with open(json_path, 'w') as file:
        json.dump(combined_data, file)

def update_data_from_message(message, csv_path, json_path):
    """
    Processes a message to extract data, updates a CSV file, and saves the updated data to a JSON file.
    """
    date, data = parse_date_and_names(message)
    print('--------')
    print(data)
    print('--------')
    append_to_csv(data, date, csv_path)
    update_json(csv_path, json_path)

if __name__ == "__main__":
    print('update')
    message = """
    #接龙
    D17 12.31

    1. jerry -2.1 共-3.4
    2. Jimmy -0.7
    3. 💄ʚ 脚丫 ɞ 🐾 ᥫᩣ ➕0.6，共3（晚上不能吃赛百味）🤣
    4. 瞿俊彦 +0.2 -3.6
    5. Joyce💗 +0.1
    6. Summer樂小樂⁶⁶ 👼🏻 -0.8共-7.5
    7. Mia.L -0.8，共-5.4
    8. 叶卡卡。 +0.8
    9. Ginger姜睿辰 -0.6 共-5.4
    """
    # message = ''
    csv_path = "data/trial.csv"
    json_path = "static/data.json"
    update_data_from_message(message, csv_path, json_path)
