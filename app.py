from flask import Flask, render_template, request
import pickle
import pandas as pd
import os

app = Flask(__name__)

# Load model
MODEL_PATH = "kolkata_model.pkl"
if not os.path.exists(MODEL_PATH):
    model = None
    print("⚠️ Model file not found. Predictions won't work.")
else:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    predicted_temp = None
    forecast = []
    future_temp = []

    # Default inputs
    temp = humidity = sealevel_pressure = None
    temp_3day_avg = humidity_3day_avg = pressure_3day_avg = None
    month = day = day_of_week = year= None
    past_temp_list = []
    past_humidity_list = []
    future_humidity_list = []
    past_pressure_list = []
    future_pressure_list = []

    if request.method == "POST":
        try:
            # Parse input values
            form = request.form
            temp = float(form.get("temp"))
            humidity = float(form.get("humidity"))
            sealevel_pressure = float(form.get("sealevel_pressure"))
            temp_lag1 = float(form.get("temp_lag1"))
            humidity_lag1 = float(form.get("humidity_lag1"))
            pressure_lag1 = float(form.get("pressure_lag1"))
            temp_3day_avg = float(form.get("temp_3day_avg"))
            humidity_3day_avg = float(form.get("humidity_3day_avg"))
            pressure_3day_avg = float(form.get("pressure_3day_avg"))
            year = int(form.get("year"))
            month = int(form.get("month"))
            day = int(form.get("day"))
            day_of_week = int(form.get("day_of_week"))

            past_temp_list = [temp_lag1 - i * 0.5 for i in reversed(range(7))]
            past_humidity_list = [humidity_lag1 - i * 1.5 for i in reversed(range(7))]
            past_pressure_list = [pressure_lag1 - i * 0.8 for i in reversed(range(7))]

            input_features = {
                'temp': temp,
                'humidity': humidity,
                'sealevel_pressure': sealevel_pressure,
                'temp_lag1': temp_lag1,
                'humidity_lag1': humidity_lag1,
                'pressure_lag1': pressure_lag1,
                'temp_3day_avg': temp_3day_avg,
                'humidity_3day_avg': humidity_3day_avg,
                'pressure_3day_avg': pressure_3day_avg,
                'year': year,
                'month': month,
                'day': day,
                'day_of_week': day_of_week
            }

            feature_order = list(input_features.keys())

            for i in range(7):
                input_list = [input_features[col] for col in feature_order]
                input_df = pd.DataFrame([input_list], columns=feature_order)

                if model:
                    pred = model.predict([input_list])[0]
                else:
                    pred = 20 + i  # Mock value if model is missing

                forecast.append(round(pred, 2))
                future_humidity_list.append(round(input_features['humidity_lag1'] + i * 1.2, 2))
                future_pressure_list.append(round(input_features['pressure_lag1'] + i * 0.9, 2))

                # Update for next cycle
                input_features['temp_lag1'] = pred
                input_features['temp_3day_avg'] = (input_features['temp_3day_avg'] * 2 + pred) / 3
                input_features['humidity_lag1'] += 1.2
                input_features['humidity_3day_avg'] = (input_features['humidity_3day_avg'] * 2 + input_features['humidity_lag1']) / 3
                input_features['pressure_lag1'] += 0.9
                input_features['pressure_3day_avg'] = (input_features['pressure_3day_avg'] * 2 + input_features['pressure_lag1']) / 3
                input_features['day'] += 1
                input_features['day_of_week'] = (input_features['day_of_week'] + 1) % 7

            predicted_temp = forecast[0]
            future_temp = forecast

        except Exception as e:
            predicted_temp = f"Error: {e}"

    return render_template("index.html",
        prediction=predicted_temp,
        forecast=forecast,
        future_temp=future_temp,
        past_temp=past_temp_list,
        past_humidity=past_humidity_list,
        future_humidity=future_humidity_list,
        past_pressure=past_pressure_list,
        future_pressure=future_pressure_list,
        input_summary={
            "temp": temp,
            "humidity_3day_avg": humidity_3day_avg,
            "pressure_3day_avg": pressure_3day_avg,
            "month": month,
            "day": day,
            "day_of_week": day_of_week,
            "year": year
        }
    )

if __name__ == "__main__":
    app.run(debug=True)
