from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from pathlib import Path
import pandas as pd
import joblib
import requests


# =========================================================
# APP SETUP
# =========================================================

app = Flask(__name__)

app.secret_key = "boardmind-ai-secret-key"

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# OLLAMA SETUP
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

# Change this if your "ollama list" shows another model
OLLAMA_MODEL = "llama3.2:3b"


# =========================================================
# PROJECT PATHS
# =========================================================

MODEL_DIR = BASE_DIR / "models"

SALES_MODEL_PATH = MODEL_DIR / "sales_model.pkl"

PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"


# =========================================================
# LOAD SALES MODEL
# =========================================================

model = None
preprocessor = None


try:

    if SALES_MODEL_PATH.exists():

        model = joblib.load(
            SALES_MODEL_PATH
        )

        print("Sales model loaded successfully.")

    else:

        print("WARNING: sales_model.pkl not found.")


except Exception as e:

    print("Error loading sales model:", e)


# =========================================================
# LOAD PREPROCESSOR
# =========================================================

try:

    if PREPROCESSOR_PATH.exists():

        preprocessor = joblib.load(
            PREPROCESSOR_PATH
        )

        print("Preprocessor loaded successfully.")

    else:

        print("WARNING: preprocessor.pkl not found.")


except Exception as e:

    print("Error loading preprocessor:", e)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")


        if username == "admin" and password == "admin123":

            session["logged_in"] = True

            session["username"] = username

            return redirect(
                url_for("dashboard")
            )


        return render_template(
            "login.html",
            error="Invalid username or password"
        )


    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    data = {

        "revenue": "₹2.5 Cr",

        "profit": "₹80 L",

        "sales": "15,200",

        "employees": "245",

        "inventory": "91%",

        "risk_score": "Low"

    }


    return render_template(
        "dashboard.html",
        data=data
    )


# =========================================================
# DIGITAL TWIN
# =========================================================

@app.route("/digital-twin")
def digital_twin():

    return render_template(
        "digital-twin.html"
    )


# =========================================================
# AI BOARDROOM
# =========================================================

@app.route("/boardroom")
def boardroom():

    return render_template(
        "boardroom.html"
    )


# =========================================================
# DEBATE PAGE + OLLAMA
# =========================================================

@app.route("/debate", methods=["GET", "POST"])
def debate():

    # -----------------------------------------------------
    # OPEN DEBATE PAGE
    # -----------------------------------------------------

    if request.method == "GET":

        return render_template(
            "debate.html"
        )


    # -----------------------------------------------------
    # GET QUESTION
    # -----------------------------------------------------

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "error": "No data received."

        }), 400


    question = data.get(
        "question",
        ""
    ).strip()


    if not question:

        return jsonify({

            "success": False,

            "error":
                "Please enter a business question."

        }), 400


    # -----------------------------------------------------
    # CEO PROMPT
    # -----------------------------------------------------

    ceo_prompt = f"""

You are the CEO AI Agent of a company.

Business Question:
{question}

Analyze this decision from a CEO perspective.

Focus on:

- Business strategy
- Company growth
- Long-term impact
- Business opportunities
- Competitive advantage

Give:

1. Analysis
2. Key consideration
3. Recommended action

Keep the response concise and professional.

"""


    # -----------------------------------------------------
    # CFO PROMPT
    # -----------------------------------------------------

    cfo_prompt = f"""

You are the CFO AI Agent of a company.

Business Question:
{question}

Analyze this decision from a CFO perspective.

Focus on:

- Revenue
- Profit
- Costs
- Budget
- Cash flow
- Financial risks

Give:

1. Financial analysis
2. Financial risk
3. Recommended action

Keep the response concise and professional.

"""


    # -----------------------------------------------------
    # SALES PROMPT
    # -----------------------------------------------------

    sales_prompt = f"""

You are the Sales Head AI Agent of a company.

Business Question:
{question}

Analyze this decision from a Sales perspective.

Focus on:

- Sales growth
- Customer acquisition
- Customer retention
- Revenue
- Market opportunities
- Customer demand

Give:

1. Sales analysis
2. Sales opportunity
3. Recommended action

Keep the response concise and professional.

"""


    # -----------------------------------------------------
    # HR PROMPT
    # -----------------------------------------------------

    hr_prompt = f"""

You are the HR Head AI Agent of a company.

Business Question:
{question}

Analyze this decision from an HR perspective.

Focus on:

- Employees
- Recruitment
- Workforce planning
- Productivity
- Employee development
- Organizational impact

Give:

1. HR analysis
2. People-related risk
3. Recommended action

Keep the response concise and professional.

"""


    try:

        print("")
        print("======================================")
        print("STARTING BOARDROOM DEBATE")
        print("======================================")
        print("Question:", question)
        print("")


        # -------------------------------------------------
        # CEO
        # -------------------------------------------------

        ceo_answer = ask_ollama(
            ceo_prompt
        )


        # -------------------------------------------------
        # CFO
        # -------------------------------------------------

        cfo_answer = ask_ollama(
            cfo_prompt
        )


        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        sales_answer = ask_ollama(
            sales_prompt
        )


        # -------------------------------------------------
        # HR
        # -------------------------------------------------

        hr_answer = ask_ollama(
            hr_prompt
        )


        # -------------------------------------------------
        # FINAL BOARD DECISION
        # -------------------------------------------------

        final_prompt = f"""

You are the Final Board Decision AI.

Business Question:

{question}


CEO Opinion:

{ceo_answer}


CFO Opinion:

{cfo_answer}


Sales Head Opinion:

{sales_answer}


HR Head Opinion:

{hr_answer}


Compare all four executive opinions.

Create the final board recommendation.

Give:

1. Recommended Decision
2. Main Reason
3. Major Risk
4. Next Action

Do not repeat all four opinions.

Keep the final answer concise and professional.

"""


        final_answer = ask_ollama(
            final_prompt
        )


        print("Boardroom debate completed.")


        # -------------------------------------------------
        # SEND RESULTS TO FRONTEND
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "ceo": ceo_answer,

            "cfo": cfo_answer,

            "sales": sales_answer,

            "hr": hr_answer,

            "final": final_answer

        })


    except Exception as e:

        print(
            "Ollama Debate Error:",
            e
        )


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# OLLAMA HELPER FUNCTION
# =========================================================

def ask_ollama(prompt):

    response = requests.post(

        OLLAMA_URL,

        json={

            "model": OLLAMA_MODEL,

            "prompt": prompt,

            "stream": False

        },

        timeout=180

    )


    if response.status_code != 200:

        raise Exception(
            f"Ollama error: {response.text}"
        )


    result = response.json()


    return result.get(
        "response",
        "No response generated."
    )


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    return render_template(
        "analytics.html"
    )


# =========================================================
# REPORTS
# =========================================================

@app.route("/reports")
def reports():

    return render_template(
        "reports.html"
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
def settings():

    return render_template(
        "settings.html"
    )


# =========================================================
# DECISION HISTORY
# =========================================================

@app.route("/decision")
def decision():

    return render_template(
        "decision.html"
    )


# =========================================================
# MEETING
# =========================================================

@app.route("/meeting")
def meeting():

    return render_template(
        "meeting.html"
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.route("/notifications")
def notifications():

    return render_template(
        "notifications.html"
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    return render_template(
        "profile.html"
    )


# =========================================================
# CEO AGENT
# =========================================================

@app.route("/ceo")
def ceo():

    return render_template(
        "ceo.html"
    )


# =========================================================
# CFO AGENT
# =========================================================

@app.route("/cfo")
def cfo():

    return render_template(
        "cfo.html"
    )


# =========================================================
# SALES AGENT
# =========================================================

@app.route("/sales")
def sales():

    return render_template(
        "sales.html"
    )


# =========================================================
# HR AGENT
# =========================================================

@app.route("/hr")
def hr():

    return render_template(
        "hr.html"
    )


# =========================================================
# INDIVIDUAL AGENT CONSULTATION
# =========================================================

@app.route(
    "/agent-consult",
    methods=["POST"]
)
def agent_consult():

    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "error": "No data received."

        }), 400


    agent = data.get("agent")

    question = data.get(
        "question",
        ""
    ).strip()


    if not question:

        return jsonify({

            "success": False,

            "error":
                "Please enter a business question."

        }), 400


    prompts = {

        "ceo": """

You are the CEO AI Agent.

Focus on:

- Business strategy
- Company growth
- Major decisions
- Long-term planning
- Competitive advantage

Give analysis and recommended action.

""",

        "cfo": """

You are the CFO AI Agent.

Focus on:

- Revenue
- Profit
- Costs
- Budget
- Cash flow
- Financial risks

Give financial analysis and recommended action.

""",

        "sales": """

You are the Sales Head AI Agent.

Focus on:

- Sales growth
- Customers
- Revenue
- Market opportunities
- Customer acquisition

Give sales analysis and recommended action.

""",

        "hr": """

You are the HR Head AI Agent.

Focus on:

- Employees
- Recruitment
- Workforce
- Performance
- Employee development

Give HR analysis and recommended action.

"""

    }


    if agent not in prompts:

        return jsonify({

            "success": False,

            "error": "Invalid agent."

        }), 400


    full_prompt = f"""

{prompts[agent]}

Business Question:

{question}

Answer as the
{agent.upper()} AI Agent.

Be concise and professional.

"""


    try:

        answer = ask_ollama(
            full_prompt
        )


        return jsonify({

            "success": True,

            "agent": agent,

            "response": answer

        })


    except Exception as e:

        print(
            "Agent consultation error:",
            e
        )


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# SALES PREDICTION
# =========================================================

@app.route(
    "/predict-sales",
    methods=["POST"]
)
def predict_sales():

    if model is None:

        return jsonify({

            "success": False,

            "error":
                "Sales model is not loaded."

        }), 500


    if preprocessor is None:

        return jsonify({

            "success": False,

            "error":
                "Preprocessor is not loaded."

        }), 500


    data = request.get_json()


    if not data:

        return jsonify({

            "success": False,

            "error":
                "No data received."

        }), 400


    try:

        new_data = {

            "Age": [
                data["Age"]
            ],

            "Gender": [
                data["Gender"]
            ],

            "Product Category": [
                data["Product Category"]
            ],

            "Quantity": [
                data["Quantity"]
            ],

            "Price per Unit": [
                data["Price per Unit"]
            ]

        }


    except KeyError as e:

        return jsonify({

            "success": False,

            "error":
                f"Missing field: {e}"

        }), 400


    try:

        new_customer = pd.DataFrame(
            new_data
        )


        processed_data = (
            preprocessor.transform(
                new_customer
            )
        )


        prediction = model.predict(
            processed_data
        )


        predicted_sales = round(
            float(prediction[0]),
            2
        )


        return jsonify({

            "success": True,

            "predicted_sales":
                predicted_sales

        })


    except Exception as e:

        print(
            "Prediction error:",
            e
        )


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# TEST OLLAMA
# =========================================================

@app.route("/test-ai")
def test_ai():

    try:

        answer = ask_ollama(
            "Say: BoardMind AI is connected successfully."
        )


        return jsonify({

            "status": "SUCCESS",

            "message": answer

        })


    except Exception as e:

        return jsonify({

            "status": "ERROR",

            "message": str(e)

        }), 500


# =========================================================
# CHECK OLLAMA MODELS
# =========================================================

@app.route("/models")
def models():

    try:

        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=10
        )


        if response.status_code != 200:

            return jsonify({

                "status": "ERROR",

                "message":
                    "Unable to connect to Ollama."

            }), 500


        data = response.json()


        model_names = []


        for item in data.get(
            "models",
            []
        ):

            model_names.append(
                item.get("name")
            )


        return jsonify({

            "status": "SUCCESS",

            "models": model_names

        })


    except Exception as e:

        return jsonify({

            "status": "ERROR",

            "message": str(e)

        }), 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("")
    print("======================================")
    print("       BOARDMIND AI STARTING")
    print("======================================")
    print("")

    print(
        "Ollama Model:",
        OLLAMA_MODEL
    )

    print(
        "Ollama URL:",
        OLLAMA_URL
    )

    if model:

        print(
            "Sales ML Model: LOADED"
        )

    else:

        print(
            "Sales ML Model: NOT LOADED"
        )

    print("")
    print(
        "Open: http://127.0.0.1:5000"
    )
    print("")

    app.run(
        debug=True
    )