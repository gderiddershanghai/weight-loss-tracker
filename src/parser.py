import re
import pandas as pd

def parse_date_and_names(message):
    """
    Extracts the date and parses names and scores from a given message.

    Parameters:
        message (str): The string message containing the date and name-score pairs.

    Returns:
        tuple:
            date (str): Extracted date in 'MM.DD' format or 'Date Not Found' if no valid date is found.
            parsed_data (dict): A dictionary where keys are standard names and values are scores (float).
    """
    lines = message.split('\n')
    
    # Normalize non-standard characters for + and -
    message = message.replace('－', '-').replace('➕', '+').replace('＋', '+').replace('–', '-')

    # Extract date pattern
    date_pattern = r'\d{2}\.\d{2}(-D\d+|共|Day\d+)?'
    date = "Date Not Found"
    for line in lines:
        date_match = re.search(date_pattern, line)
        if date_match:
            date = date_match.group(0).split('-')[0]  # Extract only the 'MM.DD' part
            break

    # Mapping for name replacements
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

    # Dictionary to hold parsed data
    parsed_data = {}
    # Pattern to extract scores
    score_pattern = r"([-+]?\d*\.?\d+)"

    # Iterate through lines to find names and scores
    for line in lines[2:]:  # Assuming the first two lines are not data lines
        # Split line into parts
        parts = line.split(' ', 2)
        if len(parts) < 3:
            continue
        
        # Find the score in the line
        score_matches = re.findall(score_pattern, parts[2])
        print(score_matches)
        if score_matches:
            score = float(score_matches[1])
            # Check if there's a weird plus sign or no sign, assume negative if not specified
            if '＋' not in line and '➕' not in line and not score_matches[1].startswith(('+', '-')):
                print('score', score)
                score = -abs(score)
        else:
            score = 0.0

        # Match names using the name mapping
        for key, value in name_mapping.items():
            if key in line:
                parsed_data[value] = score
                break
            
    return date, parsed_data


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
        for name, score in data.items():
            df.at[idx, name] = score
            
    else:
        new_row = {'Date': date, **{name: 0 for name in df.columns if name != 'Date'}}
        new_row.update(data)
        df = df.append(new_row, ignore_index=True)

    df.to_csv(file_path, index=False)
    print(f"Data successfully written to {file_path}.")
