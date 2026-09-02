from flask import Flask, render_template, request, redirect, url_for

from database import init_db, get_db
from risk_engine import calculate_risk


app = Flask(__name__)

# Database create/initialize
init_db()


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Farmer Portal
@app.route("/farmer")
def farmer():
    conn = get_db()

    farmers = conn.execute(
        "SELECT * FROM farmers"
    ).fetchall()

    conn.close()

    return render_template(
        "farmer.html",
        farmers=farmers
    )


# Register Farmer
@app.route("/register-farmer", methods=["POST"])
def register_farmer():

    name = request.form["name"]
    mobile = request.form["mobile"]
    village = request.form["village"]
    block = request.form["block"]
    district = request.form["district"]

    conn = get_db()

    conn.execute("""
        INSERT INTO farmers
        (name, mobile, village, block, district)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        mobile,
        village,
        block,
        district
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("farmer"))


# Animal Registration Page
@app.route("/animal/<int:farmer_id>")
def animal_page(farmer_id):

    conn = get_db()

    farmer = conn.execute(
        "SELECT * FROM farmers WHERE id = ?",
        (farmer_id,)
    ).fetchone()

    animals = conn.execute(
        "SELECT * FROM animals WHERE farmer_id = ?",
        (farmer_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "register_animal.html",
        farmer=farmer,
        animals=animals
    )


# Register Animal
@app.route("/register-animal/<int:farmer_id>", methods=["POST"])
def register_animal(farmer_id):

    animal_type = request.form["animal_type"]
    age = request.form["age"]
    gender = request.form["gender"]

    conn = get_db()

    # Last animal ID
    last_animal = conn.execute(
        "SELECT id FROM animals ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if last_animal:
        number = last_animal["id"] + 1
    else:
        number = 1

    animal_id = f"ANM{number:03d}"

    conn.execute("""
        INSERT INTO animals
        (animal_id, farmer_id, animal_type, age, gender)
        VALUES (?, ?, ?, ?, ?)
    """, (
        animal_id,
        farmer_id,
        animal_type,
        age,
        gender
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for(
            "animal_page",
            farmer_id=farmer_id
        )
    )


# Report Symptoms Page
@app.route("/report/<animal_id>")
def report_page(animal_id):

    conn = get_db()

    animal = conn.execute("""
        SELECT animals.*, farmers.village
        FROM animals
        JOIN farmers
        ON animals.farmer_id = farmers.id
        WHERE animals.animal_id = ?
    """, (animal_id,)).fetchone()

    conn.close()

    return render_template(
        "report.html",
        animal=animal,
        result=False
    )


# Submit Symptoms Report
@app.route("/submit-report/<animal_id>", methods=["POST"])
def submit_report(animal_id):

    symptoms = request.form.getlist("symptoms")

    conn = get_db()

    animal = conn.execute("""
        SELECT animals.*, farmers.village
        FROM animals
        JOIN farmers
        ON animals.farmer_id = farmers.id
        WHERE animals.animal_id = ?
    """, (animal_id,)).fetchone()

    # Calculate risk
    risk = calculate_risk(symptoms)

    symptoms_text = ", ".join(symptoms)

    conn.execute("""
        INSERT INTO reports
        (
            animal_id,
            symptoms,
            symptom_count,
            risk_level,
            village
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        animal_id,
        symptoms_text,
        len(symptoms),
        risk,
        animal["village"]
    ))

    conn.commit()
    conn.close()

    return render_template(
        "report.html",
        animal=animal,
        result=True,
        risk=risk,
        symptoms=symptoms
    )


# Veterinary Dashboard
@app.route("/dashboard")
def dashboard():

    conn = get_db()

    # Total animals
    total_animals = conn.execute(
        "SELECT COUNT(*) AS count FROM animals"
    ).fetchone()["count"]

    # Total cases
    total_cases = conn.execute(
        "SELECT COUNT(*) AS count FROM reports"
    ).fetchone()["count"]

    # High risk
    high_risk = conn.execute("""
        SELECT COUNT(*) AS count
        FROM reports
        WHERE risk_level = 'High'
    """).fetchone()["count"]

    # Medium risk
    medium_risk = conn.execute("""
        SELECT COUNT(*) AS count
        FROM reports
        WHERE risk_level = 'Medium'
    """).fetchone()["count"]

    # Low risk
    low_risk = conn.execute("""
        SELECT COUNT(*) AS count
        FROM reports
        WHERE risk_level = 'Low'
    """).fetchone()["count"]

    # Village-wise cases
    village_cases = conn.execute("""
        SELECT village, COUNT(*) AS cases
        FROM reports
        GROUP BY village
        ORDER BY cases DESC
    """).fetchall()

    # Recent reports
    recent_reports = conn.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_animals=total_animals,
        total_cases=total_cases,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        village_cases=village_cases,
        recent_reports=recent_reports
    )


# Run Flask Server
if __name__ == "__main__":
    app.run(debug=True)