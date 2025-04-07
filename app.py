from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

# Load the model
model = pickle.load(open("weather_prediction_model.pkl", "rb"))

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    forecast = []

    if request.method == "POST":
        try:
            # Extract all 12 input features
            temp_lag1 = float(request.form.get("temp_lag1"))
            humidity_lag1 = float(request.form.get("humidity_lag1"))
            pressure_lag1 = float(request.form.get("pressure_lag1"))
            temp_3day_avg = float(request.form.get("temp_3day_avg"))
            humidity_3day_avg = float(request.form.get("humidity_3day_avg"))
            pressure_3day_avg = float(request.form.get("pressure_3day_avg"))
            month = int(request.form.get("month"))
            day = int(request.form.get("day"))
            day_of_week = int(request.form.get("day_of_week"))
            cloudcover_3day_avg = float(request.form.get("cloudcover_3day_avg"))
            windspeed_3day_avg = float(request.form.get("windspeed_3day_avg"))
            solarradiation_3day_avg = float(request.form.get("solarradiation_3day_avg"))

            # Initial input features dictionary
            input_features = {
                'temp_lag1': temp_lag1,
                'humidity_lag1': humidity_lag1,
                'pressure_lag1': pressure_lag1,
                'temp_3day_avg': temp_3day_avg,
                'humidity_3day_avg': humidity_3day_avg,
                'pressure_3day_avg': pressure_3day_avg,
                'month': month,
                'day': day,
                'day_of_week': day_of_week,
                'cloudcover_3day_avg': cloudcover_3day_avg,
                'windspeed_3day_avg': windspeed_3day_avg,
                'solarradiation_3day_avg': solarradiation_3day_avg
            }

            # Forecast for next 7 days
            for _ in range(7):
                feature_order = [
                    'temp_lag1', 'humidity_lag1', 'pressure_lag1',
                    'temp_3day_avg', 'humidity_3day_avg', 'pressure_3day_avg',
                    'month', 'day', 'day_of_week',
                    'cloudcover_3day_avg', 'windspeed_3day_avg', 'solarradiation_3day_avg'
                ]

                input_list = [input_features[col] for col in feature_order]
                pred = model.predict([input_list])[0]
                forecast.append(round(pred, 2))

                # Simulate next day's input update
                input_features['temp_lag1'] = pred
                input_features['temp_3day_avg'] = (input_features['temp_3day_avg'] * 2 + pred) / 3
                input_features['humidity_3day_avg'] = input_features['humidity_lag1']
                input_features['pressure_3day_avg'] = input_features['pressure_lag1']

                input_features['day'] += 1
                input_features['day_of_week'] = (input_features['day_of_week'] + 1) % 7

                # Optional: keep cloudcover/wind/solar the same or simulate if you want
                # Currently, they are held constant

            prediction = forecast[0]  # Tomorrow's prediction as primary

        except Exception as e:
            prediction = f"Error: {e}"

    return render_template("index.html", prediction=prediction, forecast=forecast)

if __name__ == "__main__":
    app.run(debug=True)
