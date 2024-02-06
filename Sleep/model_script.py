from joblib import load

def load_model(model_path):
    return load(model_path)

def predict(model, data):
    return model.predict(data)

# Example usage
model = load_model("C:/Users/mainf/OneDrive/Desktop/Fitness Data Project/Sleep/Models&Metrics/Activity_level_model/BEST_MODEL.joblib")
# You can now call predict(model, data) to make predictions

print(model)
