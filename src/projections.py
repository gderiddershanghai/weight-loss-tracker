import numpy as np

def calculate_cumulative_projections(values, last_cumulative, weights=[0.4, 0.3, 0.2, 0.1, 0.0], num_projections=5):
    """
    Calculate cumulative projections based on weighted averages.

    Args:
        values (list): List of daily differences (raw values) for a user.
        last_cumulative (float): The last cumulative value to start projections from.
        weights (list): List of weights for the 5-day weighted average.
        num_projections (int): Number of future projections to calculate.

    Returns:
        list: A list of cumulative projections.
    """
    if len(values) < 5:
        raise ValueError("Not enough values to compute projections. Need at least 5.")

    # Initialize the list of cumulative projections with the last cumulative value
    cumulative_projections = [last_cumulative]

    # Generate future projections
    for _ in range(num_projections):
        last_five = np.array(values[-5:])  # Take the last 5 values
        proj_diff = round(last_five @ np.array(weights), 2)  # Weighted average for the projection
        values.append(proj_diff)  # Add the projection to the raw values
        new_cumulative = np.round(cumulative_projections[-1] + proj_diff, 2)  # Update cumulative projection
        cumulative_projections.append(new_cumulative)

    return cumulative_projections[1:]  # Skip the initial value (starting point)
