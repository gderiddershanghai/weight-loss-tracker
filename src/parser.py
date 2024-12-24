import re
import pandas as pd

def parse_date_and_names(message):
    """
    Extracts the date and parses names and scores from a given message.

    The function searches for a date in the format 'MM.DD-DX' within the message,
    and parses specified names mapped to their scores. It expects the message to be formatted
    with the date on one of the first few lines followed by lines containing names and scores.

    Parameters:
        message (str): The string message containing the date and name-score pairs.

    Returns:
        tuple:
            date (str): Extracted date in 'MM.DD' format or 'Date Not Found' if no valid date is found.
            parsed_data (dict): A dictionary where keys are standard names and values are scores (float).
    """
    lines = message.split('\n')
    
    date_pattern = r'\d{2}\.\d{2}-D\d+'
    for line in lines:
        date_match = re.search(date_pattern, line)
        if date_match:
            date = date_match.group(0).split('-')[0] if date_match else 'Date Not Found'
            break

    name_mapping = {
        "💄ʚ 脚丫 ɞ 🐾": "Jenny",
        "叶卡卡": "Blue",
        "Summer樂": "Summer G",
        "joker": "Yoyo",
        "jerry": "Jerry",
        "Jimmy": "Jimmy",
        "Esther Gu": "Esther",
        "Barry": "Barry",
        "Joyce💗": "Joyce",
        "Mia.L": "Mia",
        "Sofya™": "Sofya",
        "Ginger姜睿辰": "Ginger",
        "瞿俊彦": "Nick",
        "fifi": "Fifi"
    }

    parsed_data = {}
    pattern = r"([-+]?[0-9]*\.?[0-9]+)" 

    for line in lines[2:]: 
        parts = line.split(' ', 2)
        if len(parts) < 3:
            continue
        score = re.findall(pattern, parts[2])
        score = float(score[0]) if score else 0.0 

        for key, value in name_mapping.items():
            if key in line:  
                parsed_data[value] = score
                break

    return date, parsed_data

import pandas as pd

def append_to_csv(data, date, file_path):
    """
    Appends or updates scores in a CSV file based on provided data for a specific date.

    If the date exists in the CSV, the function updates the scores for that date.
    If the date does not exist, a new row is added. Names not provided in the data
    receive a default score of 0 for that date.

    Parameters:
        data (dict): A dictionary containing names as keys and scores as values.
        date (str): The date for which the scores are being recorded.
        file_path (str): The path to the CSV file where the data is to be written.

    Returns:
        None: The function does not return any value but prints a success message or a file not found error.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File {file_path} not found. Please check the file path.")
        return

    if date in df['Date'].values:
        idx = df[df['Date'] == date].index[0]
        for name in df.columns:
            if name != 'Date':
                df.at[idx, name] = 0
        for name, score in data.items():
            df.at[idx, name] = score
    else:
        new_row = {'Date': date, **{name: 0 for name in df.columns if name != 'Date'}}
        new_row.update(data)
        df = df.append(new_row, ignore_index=True)

    df.to_csv(file_path, index=False)
    print(f"Data successfully written to {file_path}.")
