# import numpy as np

# def calculate_cumulative_projections(values, 
#                                      last_cumulative, 
#                                      weights = [0.08, 0.15, 0.12, 0.18, 0.12, 0.16, 0.19],
#                                      num_projections=5):
#     """
#     Calculate cumulative projections based on weighted averages.

#     Args:
#         values (list): List of daily differences (raw values) for a user.
#         last_cumulative (float): The last cumulative value to start projections from.
#         weights (list): List of weights for the 5-day weighted average.
#         num_projections (int): Number of future projections to calculate.

#     Returns:
#         list: A list of cumulative projections.
#     """
#     if len(values) < 5:
#         raise ValueError("Not enough values to compute projections. Need at least 5.")

#     # Initialize the list of cumulative projections with the last cumulative value
#     cumulative_projections = [last_cumulative]
    
#     motivation_factor = 1.1
#     randomness_scale = 0.6
    
#     # Generate future projections
#     for _ in range(num_projections):
#         mean = np.mean(values)
#         std = np.std(values)
#         last_seven = np.array(values[-7:])  # Take the last 7 values
#         proj_diff = round(last_seven @ np.array(weights), 2)  # Weighted average for the projection
#         # print(proj_diff, '--------')
#         if proj_diff>0:
#             proj_diff = proj_diff-abs(np.random.normal(mean, std**2) )
#         else:
#             # random_adjustment = 1 + np.random.normal(0, randomness_scale)  # Generate a random factor around 1
#             # proj_diff *= motivation_factor * random_adjustment  # Apply the combined random and motivation factor
#             proj_diff = proj_diff + np.random.normal(np.random.normal(mean, std**2))
#         values.append(proj_diff)  # Add the projection to the raw values
#         new_cumulative = np.round(cumulative_projections[-1] + proj_diff, 2)  # Update cumulative projection
#         cumulative_projections.append(new_cumulative)

#     return cumulative_projections[1:]  # Skip the initial value (starting point)
# import numpy as np

# def calculate_cumulative_projections(values, last_cumulative, weights=[0.08, 0.15, 0.12, 0.18, 0.12, 0.16, 0.19]):
#     """
#     Calculate cumulative projections based on weighted averages.

#     Args:
#         values (list): List of daily differences (raw values) for a user.
#         last_cumulative (float): The last cumulative value to start projections from.
#         weights (list): List of weights for a 7-day weighted average.

#     Returns:
#         list: A list of cumulative projections.
#     """
#     if len(values) < len(weights):
#         raise ValueError(f"Not enough values to compute projections. Need at least {len(weights)}.")

#     cumulative_projections = [last_cumulative]
#     mean = np.mean(values)
#     std = np.std(values)
#     print(mean, std, '--------')
#     # Generate future projections
#     for _ in range(len(weights)):
#         last_values = np.array(values[-7:])  # Ensure we're always using the last 7 values
#         proj_diff = np.dot(last_values, weights)  # Weighted average for the projection
#         if proj_diff>0:
#             proj_diff *= 0.75
#         proj_diff += 0.5*np.random.normal(0, std)  # Apply random adjustment based on the standard deviation
#         values.append(proj_diff)  # Update raw values list
#         new_cumulative = round(cumulative_projections[-1] + proj_diff, 2)
#         cumulative_projections.append(new_cumulative)

#     return cumulative_projections[1:]  # Skip the initial value to return only projections
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def calculate_cumulative_projections(values, last_cumulative, num_forecasts=5):
    """
    Forecasting using ARIMA model with random shocks added to the predictions,
    and updating cumulative values based on these forecasts.

    Args:
        values (list or array): Historical daily differences (raw values) for a user.
        last_cumulative (float): The last cumulative value to start projections from.
        num_forecasts (int): Number of future data points to forecast.

    Returns:
        list: A list of cumulative projections.
    """
    # Fit an ARIMA model on the differences
    model = ARIMA(values, order=(3, 0, 2))  # ARIMA model order can be tuned based on AIC/BIC
    fitted_model = model.fit()
    
    # Forecast future differences
    forecasted_differences = fitted_model.forecast(steps=num_forecasts)

    # Prepare to update cumulative totals
    cumulative_projections = [last_cumulative]
    std_dev = np.std(values)  # Standard deviation for adding randomness

    # Update cumulative totals with forecasted differences
    for diff in forecasted_differences:
        random_shock = np.random.normal(0.0, std_dev * 0.75)  # Adding 75% of std deviation as random shock
        new_value = cumulative_projections[-1] + diff + random_shock
        cumulative_projections.append(new_value)
    print(cumulative_projections)
    return cumulative_projections[1:]
