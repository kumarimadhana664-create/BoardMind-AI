from flask import Flask, request, jsonify, render_template
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

model = joblib.load("models/sales_model.pkl")
preprocessor = joblib.load("models/preprocessor.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():

    dashboard_data = {
        "revenue": "₹2.5 Cr",
        "profit": "₹80 L",
        "sales": "15,200",
        "employees": 245,
        "inventory": "91%",
        "risk": "Low"
    }

    return render_template(
        "dashboard.html",
        data=dashboard_data
    )

@app.route("/predict-sales", methods=["POST"])
def predict_sales():

    data = request.json

    new_data = {
        "Age": [data["Age"]],
        "Gender": [data["Gender"]],
        "Product Category": [data["Product Category"]],
        "Quantity": [data["Quantity"]],
        "Price per Unit": [data["Price per Unit"]]
    }

    new_customer = pd.DataFrame(new_data)

    processed_data = preprocessor.transform(new_customer)

    prediction = model.predict(processed_data)

    return jsonify({
        "predicted_sales": round(float(prediction[0]), 2)
    })

@app.route("/boardroom")
def boardroom():
    return render_template("boardroom.html")


@app.route("/debate")
def debate():
    return render_template("debate.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Temporary login
        if email == "admin@gmail.com" and password == "admin123":

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)