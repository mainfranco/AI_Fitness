import numpy as np
from model_script import load_model, predict

# Load the model
model = load_model("C:/Users/mainf/OneDrive/Desktop/Fitness Data Project/Sleep/Models&Metrics/Activity_level_model/BEST_MODEL.joblib")

# Example data point
data_point = np.array([[775., 454.8, 5.0300002098, 264., 15506., 9.8800001144, 432.6, 2035.]])  

# Get prediction
prediction = predict(model, data_point) / 60
print("Original Prediction:", prediction)

# Define the feature ranges, excluding 'TotalMinutesAsleep_Weekly' and 'TotalTimeInBed_Weekly'
feature_ranges = {
    'SedentaryMinutes': (0, 480),
    'LightActiveDistance': (0, float('inf')),
    'LightlyActiveMinutes': (15, 60),
    'TotalSteps': (7000, 12000),
    'TotalDistance': (0, float('inf')),
    'Calories': (2000, 2500)
}

# Store the current and suggested values
suggested_features = {}
for i, (key, (min_val, max_val)) in enumerate(feature_ranges.items()):
    current_value = data_point[0][i]
    new_value = current_value
    if current_value > max_val:
        new_value = max_val
    elif current_value < min_val:
        new_value = min_val
    suggested_features[key] = {'current': current_value, 'recommended': new_value}

# Include the unchanged features
suggested_features['TotalMinutesAsleep_Weekly'] = {'current': data_point[0][6], 'recommended': data_point[0][6]}
suggested_features['TotalTimeInBed_Weekly'] = {'current': data_point[0][7], 'recommended': data_point[0][7]}

# Create the suggested activity array
suggested_activity = np.array([[values['recommended'] for key, values in suggested_features.items()]])

# Predict the projected sleep hours
projected_sleep_hours = predict(model, suggested_activity) / 60
print(f"Projected hours of sleep: {projected_sleep_hours}")
print(f"Projected improvement: {(projected_sleep_hours - prediction)}: Hours")

# Print the suggested features with current and recommended values
for key, values in suggested_features.items():
    print(f"{key}: Current - {values['current']}, Recommended - {values['recommended']}")



