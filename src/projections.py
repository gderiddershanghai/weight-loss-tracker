import numpy as np

def calculate_cumulative_projections(values, 
                                     last_cumulative, 
                                     weights = [0.08, 0.15, 0.12, 0.18, 0.12, 0.16, 0.19],
                                     num_projections=5):
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
    
    motivation_factor = 1.1
    randomness_scale = 0.6
    
    # Generate future projections
    for _ in range(num_projections):
        last_seven = np.array(values[-7:])  # Take the last 7 values
        proj_diff = round(last_seven @ np.array(weights), 2)  # Weighted average for the projection
        # print(proj_diff, '--------')
        if proj_diff>0:
            proj_diff = proj_diff-abs(np.random.normal(-0.25, randomness_scale) )
        else:
            # random_adjustment = 1 + np.random.normal(0, randomness_scale)  # Generate a random factor around 1
            # proj_diff *= motivation_factor * random_adjustment  # Apply the combined random and motivation factor
            proj_diff = proj_diff + np.random.normal(0.05, randomness_scale)
        values.append(proj_diff)  # Add the projection to the raw values
        new_cumulative = np.round(cumulative_projections[-1] + proj_diff, 2)  # Update cumulative projection
        cumulative_projections.append(new_cumulative)

    return cumulative_projections[1:]  # Skip the initial value (starting point)
