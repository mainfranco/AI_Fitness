import numpy as np
from model_script import load_model, predict

# Load the model
model = load_model("C:/Users/mainf/OneDrive/Desktop/Fitness Data Project/Sleep/Models&Metrics/Activity_level_model/BEST_MODEL.joblib")

# Example data point
data_point = np.array([[1265,523.3333333333,0.349999994,34,3702,2.4800000191,502,1792]])  

# Get prediction
prediction = predict(model, data_point) / 60
print("Prediction:", prediction)

feature_ranges = {
    'SedentaryMinutes': (0, 480),
    'TotalTimeInBed_Weekly': (49*60, 63*60),
    'LightActiveDistance': (0, float('inf')),
    'LightlyActiveMinutes': (15, 60),
    'TotalSteps': (7000, 12000),
    'TotalDistance': (0, float('inf')),
    'TotalMinutesAsleep_Weekly': (49*60, 63*60),
    'Calories': (2000, 2500)
}
feature_range_outcomes = []

improve = .25
for i, (key, (min_val, max_val)) in enumerate(feature_ranges.items()):
    feature_value = data_point[0][i]  # Accessing the ith element of the first row
    
    if feature_value > max_val:
        difference = feature_value - max_val
        feature_range_outcomes.append((difference,"ABOVE"))

    elif feature_value <= min_val:
        difference = min_val - feature_value
        in_range = True
        feature_range_outcomes.append((difference,"BELOW"))
    else:
        feature_range_outcomes.append((feature_value,"INRANGE"))

new_values = []

for i in feature_range_outcomes:
    value = i[0]
    status = i[1]

    if status == 'ABOVE':
        new_value = value - (improve * value)
            
        new_values.append(new_value)
    elif status == 'BELOW':
        new_value = value + (improve * value)
        new_values.append(new_value)
    else:
        new_values.append(value)

suggested_activity = np.array([new_values])
projected_sleep_hours = model.predict(suggested_activity) / 60


print(f"Projected hours of sleep: {projected_sleep_hours}")
print(f"Projected improvement: {(projected_sleep_hours - prediction)}: Hours")

suggested_activity_level = {
    'SedentaryMinutes': 0,
    'TotalTimeInBed_Weekly': 0,
    'LightActiveDistance': 0,
    'LightlyActiveMinutes': 0,
    'TotalSteps': 0,
    'TotalDistance':0,
    'TotalMinutesAsleep_Weekly': 0,
    'Calories': 0
}

print(suggested_activity)
i = 0
for key, value in suggested_activity_level.items():
    suggested_activity_level[key] = new_values[i]
    i += 1


print(suggested_activity_level)


