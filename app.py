from flask import Flask, render_template, jsonify
import pandas as pd
from src.projections import calculate_cumulative_projections
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Load data
    data_path = "data/trial.csv"
    df = pd.read_csv(data_path)
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
        if last_day > 31:  # Simplistic month rollover logic
            last_day = 1
            last_month += 1
        if last_month > 12:
            last_month = 1
        future_dates.append(f"{last_month:02d}.{last_day:02d}")

    extended_dates = df["Date"].tolist() + future_dates

    # Add projections
    projections = {}
    for col in df.columns[1:]:
        values = df[col].values.tolist()  # Raw differences
        last_cumulative = cumulative_df[col].values[-1]  # Last cumulative value
        projections[col] = calculate_cumulative_projections(values, last_cumulative)

    # Combine data for the frontend
    combined_data = {
        "dates": extended_dates,
        "raw_values": df.iloc[:, 1:].to_dict(orient="list"),
        "cumulative_values": cumulative_df.iloc[:, 1:].to_dict(orient="list"),
        "projections": projections,
    }

    # Save combined data to a file in the specified path
    output_path = "/home/ginger/code/gderiddershanghai/weight-loss/static/data.json"
    with open(output_path, 'w') as file:
        json.dump(combined_data, file)

    return "Data updated and saved successfully!"


if __name__ == "__main__":
    app.run(debug=True)
