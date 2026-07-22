import os
import uuid
import json
import sqlite3
from datetime import datetime, timedelta

import numpy as np
import tensorflow as tf

from database import save_scan, get_connection
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


from auth import auth

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dermavision_secret_key")
app.register_blueprint(auth)


UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


MODEL_PATH = "model/best_model.keras"

model = tf.keras.models.load_model(MODEL_PATH)


class_names = [
    "Actinic keratosis",
    "Atopic Dermatitis",
    "Benign keratosis",
    "Dermatofibroma",
    "Melanocytic nevus",
    "Melanoma",
    "Squamous cell carcinoma",
    "Tinea Ringworm Candidiasis",
    "Vascular lesion"
]


disease_info = {

    "Actinic keratosis": {
        "description": "A rough, scaly skin lesion mainly caused by long-term ultraviolet exposure.",
        "symptoms": [
                   "Rough patches",
                     "dryness",
                     "redness", 
                     "itching",
                     "changes in skin texture."
        ],
        "causes": ["Long-term sun exposure and UV radiation."],
        "precautions": [
            "Use sunscreen regularly.",
            "Avoid prolonged direct sunlight.",
            "Wear protective clothing outdoors.",
            "Consult a dermatologist for changes."
        ]
    },

    "Atopic Dermatitis": {
        "description": "An inflammatory skin condition causing dry and itchy skin.",
        "symptoms": [
            "Dryness", 
            "itching", 
            "redness", 
            "irritation", 
            "rashes"
        ],
        "causes": ["Genetic factors", "immune response", "allergens", "environmental triggers"],
        "precautions": [
            "Keep skin moisturized.",
            "Avoid skin irritants.",
            "Use gentle skincare products.",
            "Follow medical advice."
        ]
    },

    "Benign keratosis": {
        "description": "A non-cancerous skin growth appearing as rough or raised patches.",
        "symptoms": ["Brown or black raised skin growths"],
        "causes": ["Age-related skin changes and genetic factors."],
        "precautions": [
            "Monitor changes in size and color.",
            "Protect skin from sunlight.",
            "Seek medical advice if changes occur."
        ]
    },

    "Dermatofibroma": {
        "description": "A harmless skin growth formed due to skin cell reactions.",
        "symptoms": ["Small firm bumps that may appear brown or reddish"],
        "causes": ["Minor injuries", "insect bites", "or unknown causes."],
        "precautions": [
            "Avoid scratching.",
            "Monitor changes.",
            "Consult a dermatologist if painful."
        ]
    },

    "Melanocytic nevus": {
        "description": "A common mole formed by pigment-producing cells.",
        "symptoms": ["Colored spots or raised marks on skin"],
        "causes": ["Genetics and sun exposure."],
        "precautions": [
            "Check moles regularly.",
            "Avoid excessive UV exposure.",
            "Consult doctor if changes occur."
        ]
    },

    "Melanoma": {
        "description": "A serious skin cancer developing from pigment-producing cells.",
        "symptoms": [
            "Changes in mole size",
            "shape",
            "color", 
            "bleeding",
            "irregular borders"
        ],
        "causes": ["UV exposure", "genetic factors", "and cell mutations."],
        "precautions": [
            "Use sunscreen.",
            "Avoid excessive sunlight.",
            "Perform regular skin checks.",
            "Seek medical attention early."
        ]
    },

    "Squamous cell carcinoma": {
        "description": "A skin cancer affecting squamous cells of the skin.",
        "symptoms": [
            "Scaly patches",
            "sores",
            "redness",
            "non-healing growths"
        ],
        "causes": ["UV radiation", "chronic skin damage."],
        "precautions": [
            "Protect skin from sunlight.",
            "Use sunscreen.",
            "Monitor unusual changes.",
            "Consult a dermatologist."
        ]
    },

    "Tinea Ringworm Candidiasis": {
        "description": "A fungal infection causing itchy and irritated skin patches.",
        "symptoms": [
            "Circular rashes",
            "itching",
            "redness",
            "scaling"
        ],
        "causes": ["Fungal growth", "moisture", "and infected contact."],
        "precautions": [
            "Keep skin dry.",
            "Maintain hygiene.",
            "Avoid sharing personal items.",
            "Use antifungal treatment."
        ]
    },

    "Vascular lesion": {
        "description": "A skin abnormality related to blood vessels.",
        "symptoms": [
            "Red",
            "purple",
            "or bluish marks"
        ],
        "causes": ["Changes in blood vessel development."],
        "precautions": [
            "Monitor changes.",
            "Protect affected areas.",
            "Consult dermatologist when needed."
        ]
    }

}


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # User personalization
    user_id = session.get("user_id")
    user_name = session.get("user_name") or session.get("full_name") or session.get("username") or request.args.get("user") or "User"

    if user_id:
        user_clause = "WHERE user_id = ?"
        user_params = (user_id,)
    else:
        user_clause = "WHERE (user_id IS NULL OR user_id = '')"
        user_params = ()

    # Total Scans
    cursor.execute(f"SELECT COUNT(*) FROM scans {user_clause}", user_params)
    total_scans = cursor.fetchone()[0]

    # Average Confidence
    cursor.execute(f"SELECT AVG(confidence) FROM scans {user_clause}", user_params)
    avg_confidence = cursor.fetchone()[0]
    avg_confidence = round(avg_confidence, 2) if avg_confidence is not None else 0

    # Latest Scan
    cursor.execute(f"SELECT * FROM scans {user_clause} ORDER BY scan_date DESC LIMIT 1", user_params)
    latest_scan = cursor.fetchone()

    # Recent scans (up to 10 for the searchable/sortable table)
    cursor.execute(f"SELECT * FROM scans {user_clause} ORDER BY scan_date DESC LIMIT 10", user_params)
    recent_scans = cursor.fetchall()

    # Overall Risk Level calculation
    high_risk_diseases = ["Melanoma", "Squamous cell carcinoma", "Actinic keratosis"]
    moderate_risk_diseases = ["Atopic Dermatitis", "Tinea Ringworm Candidiasis"]

    overall_risk_level = "Low Risk"
    risk_color = "green"

    if latest_scan:
        disease = latest_scan["disease"]
        if disease in high_risk_diseases:
            overall_risk_level = "High Risk"
            risk_color = "red"
        elif disease in moderate_risk_diseases:
            overall_risk_level = "Moderate Risk"
            risk_color = "amber"

    # Risk Indicators Breakdown Counts
    cursor.execute(f"SELECT disease, COUNT(*) as count FROM scans {user_clause} GROUP BY disease", user_params)
    disease_counts_rows = cursor.fetchall()

    high_risk_count = 0
    moderate_risk_count = 0
    low_risk_count = 0

    disease_labels = []
    disease_counts = []

    for row in disease_counts_rows:
        d_name = row["disease"]
        cnt = row["count"]
        disease_labels.append(d_name)
        disease_counts.append(cnt)

        if d_name in high_risk_diseases:
            high_risk_count += cnt
        elif d_name in moderate_risk_diseases:
            moderate_risk_count += cnt
        else:
            low_risk_count += cnt

    # Weekly Activity Chart Data (Last 7 Days)
    weekly_labels = []
    weekly_counts = []
    today = datetime.now().date()

    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_str = day_date.strftime("%Y-%m-%d")
        day_label = day_date.strftime("%a (%m/%d)")

        if user_id:
            cursor.execute("SELECT COUNT(*) FROM scans WHERE user_id = ? AND strftime('%Y-%m-%d', scan_date) = ?", (user_id, day_str))
        else:
            cursor.execute("SELECT COUNT(*) FROM scans WHERE (user_id IS NULL OR user_id = '') AND strftime('%Y-%m-%d', scan_date) = ?", (day_str,))
        cnt = cursor.fetchone()[0]

        weekly_labels.append(day_label)
        weekly_counts.append(cnt)

    # Monthly Confidence Trend Chart Data
    cursor.execute(f"""
        SELECT strftime('%Y-%m', scan_date) as month, ROUND(AVG(confidence), 2) as avg_conf
        FROM scans
        {user_clause}
        GROUP BY month
        ORDER BY month ASC
    """, user_params)
    monthly_rows = cursor.fetchall()
    monthly_labels = [row["month"] for row in monthly_rows]
    monthly_confidences = [row["avg_conf"] for row in monthly_rows]

    connection.close()

    # Dynamic Health Tip / Personal Insights
    health_tip = {
        "title": "Healthy Skin Insights",
        "message": "Continue performing regular skin self-examinations and schedule periodic check-ups with a dermatologist."
    }

    if latest_scan:
        disease = latest_scan["disease"]
        tips = {
            "Actinic keratosis": {
                "title": "☀ Sun Protection Recommendation",
                "message": "Actinic keratosis is associated with UV exposure. Apply SPF 30+ broad-spectrum sunscreen daily and avoid direct sun peak hours."
            },
            "Atopic Dermatitis": {
                "title": "💧 Moisture Barrier Guidance",
                "message": "Keep affected skin hydrated with non-scented emollients. Avoid harsh chemicals or known contact allergens."
            },
            "Benign keratosis": {
                "title": "🔍 Observation Tip",
                "message": "Benign keratosis growths are non-cancerous. Monitor for changes in color or size during regular check-ups."
            },
            "Dermatofibroma": {
                "title": "🩹 Skin Protection Tip",
                "message": "Avoid scratching or friction over dermatofibromas. Consult a dermatologist if lesions become uncomfortable."
            },
            "Melanocytic nevus": {
                "title": "🧴 ABCDE Mole Check",
                "message": "Regularly check moles using the ABCDE rule (Asymmetry, Border, Color, Diameter, Evolving) and protect from UV rays."
            },
            "Melanoma": {
                "title": "⚠ Urgent Dermatological Evaluation",
                "message": "Melanoma requires prompt professional medical evaluation. We strongly advise scheduling a clinical consultation."
            },
            "Squamous cell carcinoma": {
                "title": "☀ Priority Dermatologist Appointment",
                "message": "Schedule a clinical examination with a dermatologist to evaluate squamous cell carcinoma treatment options."
            },
            "Tinea Ringworm Candidiasis": {
                "title": "🧼 Antifungal & Hygiene Routine",
                "message": "Maintain clean and dry skin conditions, avoid sharing personal items, and follow prescribed antifungal treatments."
            },
            "Vascular lesion": {
                "title": "❤️ Vascular Monitoring",
                "message": "Monitor any change in color, shape, or bleeding. Consult a medical professional if rapid changes occur."
            }
        }
        health_tip = tips.get(disease, health_tip)

    return render_template(
        "dashboard.html",
        user_name=user_name,
        total_scans=total_scans,
        avg_confidence=avg_confidence,
        latest_scan=latest_scan,
        overall_risk_level=overall_risk_level,
        risk_color=risk_color,
        high_risk_count=high_risk_count,
        moderate_risk_count=moderate_risk_count,
        low_risk_count=low_risk_count,
        recent_scans=recent_scans,
        disease_labels=disease_labels,
        disease_counts=disease_counts,
        weekly_labels_json=json.dumps(weekly_labels),
        weekly_counts_json=json.dumps(weekly_counts),
        monthly_labels_json=json.dumps(monthly_labels),
        monthly_confidences_json=json.dumps(monthly_confidences),
        health_tip=health_tip
    )


@app.route("/report/<int:scan_id>")
def report(scan_id):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    user_id = session.get("user_id")

    if user_id:
        cursor.execute("SELECT * FROM scans WHERE id=? AND user_id=?", (scan_id, user_id))
    else:
        cursor.execute("SELECT * FROM scans WHERE id=? AND (user_id IS NULL OR user_id='')", (scan_id,))

    scan = cursor.fetchone()

    connection.close()

    if scan is None:

        return "Report not found or unauthorized.", 404

    info = disease_info[scan["disease"]]

    image_url = "/static/" + scan["image"]

    return render_template(

        "result.html",

        image_path=scan["image"],

        image_url=image_url,

        disease=scan["disease"],

        confidence=scan["confidence"],

        disease_info=info

    )
    
@app.route("/download_pdf/<int:scan_id>")
def download_pdf(scan_id):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    user_id = session.get("user_id")

    if user_id:
        cursor.execute("SELECT * FROM scans WHERE id=? AND user_id=?", (scan_id, user_id))
    else:
        cursor.execute("SELECT * FROM scans WHERE id=? AND (user_id IS NULL OR user_id='')", (scan_id,))

    scan = cursor.fetchone()

    connection.close()

    if scan is None:
        return "Report not found or unauthorized.", 404

    info = disease_info[scan["disease"]]

    pdf_path = f"static/reports/report_{scan_id}.pdf"

    os.makedirs("static/reports", exist_ok=True)

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(pdf_path)

    story = []

    story.append(Paragraph("<b>DermaVision AI</b>", styles["Title"]))
    story.append(Paragraph("AI Skin Analysis Report", styles["Heading2"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(
        f"<b>Disease:</b> {scan['disease']}",
        styles["BodyText"]
    ))

    story.append(Paragraph(
        f"<b>Confidence:</b> {scan['confidence']}%",
        styles["BodyText"]
    ))

    story.append(Paragraph(
        f"<b>Scan Date:</b> {scan['scan_date']}",
        styles["BodyText"]
    ))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(
        "<b>Description</b>",
        styles["Heading2"]
    ))

    story.append(Paragraph(
        info["description"],
        styles["BodyText"]
    ))

    story.append(Paragraph(
        "<br/><b>Symptoms</b>",
        styles["Heading2"]
    ))

    for symptom in info["symptoms"]:
        story.append(
            Paragraph(f"• {symptom}", styles["BodyText"])
        )

    story.append(Paragraph(
        "<br/><b>Precautions</b>",
        styles["Heading2"]
    ))

    for precaution in info["precautions"]:
        story.append(
            Paragraph(f"• {precaution}", styles["BodyText"])
        )

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(
        Paragraph(
            "<b>Medical Disclaimer</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "This report is AI-generated and should not replace professional medical advice.",
            styles["BodyText"]
        )
    )

    document.build(story)

    return send_file(
        pdf_path,
        as_attachment=True
    )
    
@app.route("/delete_scan/<int:scan_id>")
def delete_scan(scan_id):

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    user_id = session.get("user_id")

    if user_id:
        cursor.execute("SELECT image FROM scans WHERE id=? AND user_id=?", (scan_id, user_id))
    else:
        cursor.execute("SELECT image FROM scans WHERE id=? AND (user_id IS NULL OR user_id='')", (scan_id,))

    scan = cursor.fetchone()

    if scan:

        image_path = os.path.join("static", scan["image"])

        if os.path.isfile(image_path):
            os.remove(image_path)

        if user_id:
            cursor.execute("DELETE FROM scans WHERE id=? AND user_id=?", (scan_id, user_id))
        else:
            cursor.execute("DELETE FROM scans WHERE id=? AND (user_id IS NULL OR user_id='')", (scan_id,))

        connection.commit()

    connection.close()

    return redirect(url_for("history"))

@app.route("/progress")
def progress():
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    user_id = session.get("user_id")

    if user_id:
        base_clause = "WHERE user_id = ?"
        base_params = [user_id]
    else:
        base_clause = "WHERE (user_id IS NULL OR user_id = '')"
        base_params = []

    # Fetch distinct diseases for condition filtering
    cursor.execute(f"SELECT DISTINCT disease FROM scans {base_clause} ORDER BY disease ASC", tuple(base_params))
    disease_rows = cursor.fetchall()
    available_diseases = [row["disease"] for row in disease_rows]

    selected_disease = request.args.get("disease", type=str, default="").strip()

    # Filter scans by selected disease if specified and not 'all'
    if selected_disease and selected_disease != "all":
        if user_id:
            cursor.execute("SELECT * FROM scans WHERE user_id = ? AND disease = ? ORDER BY scan_date ASC", (user_id, selected_disease))
            chronological_scans = cursor.fetchall()
            cursor.execute("SELECT * FROM scans WHERE user_id = ? AND disease = ? ORDER BY scan_date DESC", (user_id, selected_disease))
            recent_scans = cursor.fetchall()
        else:
            cursor.execute("SELECT * FROM scans WHERE (user_id IS NULL OR user_id = '') AND disease = ? ORDER BY scan_date ASC", (selected_disease,))
            chronological_scans = cursor.fetchall()
            cursor.execute("SELECT * FROM scans WHERE (user_id IS NULL OR user_id = '') AND disease = ? ORDER BY scan_date DESC", (selected_disease,))
            recent_scans = cursor.fetchall()
    else:
        cursor.execute(f"SELECT * FROM scans {base_clause} ORDER BY scan_date ASC", tuple(base_params))
        chronological_scans = cursor.fetchall()

        cursor.execute(f"SELECT * FROM scans {base_clause} ORDER BY scan_date DESC", tuple(base_params))
        recent_scans = cursor.fetchall()

    total_scans = len(recent_scans)

    # Parse query params for comparison scan selection
    scan1_id = request.args.get("scan1", type=int)
    scan2_id = request.args.get("scan2", type=int)

    scan1 = None
    scan2 = None

    if total_scans >= 2:
        if scan1_id:
            for s in chronological_scans:
                if s["id"] == scan1_id:
                    scan1 = s
                    break
        if not scan1:
            scan1 = chronological_scans[0]

        if scan2_id:
            for s in chronological_scans:
                if s["id"] == scan2_id:
                    scan2 = s
                    break
        if not scan2:
            scan2 = chronological_scans[-1]

    elif total_scans == 1:
        scan1 = recent_scans[0]
        scan2 = recent_scans[0]

    # Calculate comparison deltas
    confidence_delta = 0.0
    improvement_percentage = 0.0

    if scan1 and scan2 and scan1["id"] != scan2["id"]:
        confidence_delta = round(scan2["confidence"] - scan1["confidence"], 2)
        if scan1["confidence"] > 0:
            improvement_percentage = round(((scan1["confidence"] - scan2["confidence"]) / scan1["confidence"]) * 100, 1)

    # Dynamic Skin Health Score Calculation (0 - 100)
    # Factors in the specific scan evaluated (scan2 or latest) and progression delta with scan1
    eval_scan = scan2 if scan2 else (recent_scans[0] if recent_scans else None)

    skin_health_score = 85
    health_status = "Optimal"

    if eval_scan:
        high_risk = ["Melanoma", "Squamous cell carcinoma", "Actinic keratosis"]
        moderate_risk = ["Atopic Dermatitis", "Tinea Ringworm Candidiasis"]

        disease = eval_scan["disease"]

        base_score = 85

        if disease in high_risk:
            base_score -= 20
        elif disease in moderate_risk:
            base_score -= 10
        else:
            base_score += 5

        # Incorporate comparison progression delta if 2 different scans are selected
        if scan1 and scan2 and scan1["id"] != scan2["id"]:
            if disease in high_risk or disease in moderate_risk:
                if confidence_delta < 0:
                    base_score += min(15, int(abs(confidence_delta) * 0.5))
                elif confidence_delta > 0:
                    base_score -= min(15, int(confidence_delta * 0.3))
            else:
                if abs(confidence_delta) <= 10:
                    base_score += 5

        # Factor in regular monitoring bonus
        if total_scans >= 3:
            base_score += 5

        skin_health_score = max(35, min(98, base_score))

        if skin_health_score >= 80:
            health_status = "Optimal"
        elif skin_health_score >= 60:
            health_status = "Stable"
        else:
            health_status = "Needs Evaluation"

    # Generate AI Progress Summary Insights
    ai_summary_title = "AI Recovery Analysis"
    if total_scans >= 2 and scan1 and scan2:
        if scan1["id"] == scan2["id"]:
            ai_summary_text = (
                "Please select two different scans from the dropdown menus above to view detailed before-and-after comparison analysis."
            )
        elif confidence_delta < 0:
            ai_summary_text = (
                f"Comparing scan #{scan1['id']} ({scan1['scan_date'][:10]}) to scan #{scan2['id']} ({scan2['scan_date'][:10]}), "
                f"the AI diagnostic confidence shifted by {abs(confidence_delta)}%. "
                f"The lesion indicators for {scan2['disease']} demonstrate stability. Continue routine skin care and consult a dermatologist if new symptoms develop."
            )
        elif confidence_delta > 0:
            ai_summary_text = (
                f"Between scan #{scan1['id']} ({scan1['scan_date'][:10]}) and scan #{scan2['id']} ({scan2['scan_date'][:10]}), "
                f"diagnostic confidence for {scan2['disease']} changed by +{confidence_delta}%. "
                "Higher confidence indicates distinct visual feature clarity. Schedule a professional evaluation if symptoms persist or evolve."
            )
        else:
            ai_summary_text = (
                "Scan records show consistent visual metrics across evaluation periods. "
                "Maintain regular skin monitoring and protect your skin against UV exposure."
            )
    elif total_scans == 1:
        ai_summary_text = (
            "You currently have 1 scan recorded. Complete additional scans over time to generate before-and-after comparison analytics and confidence trends."
        )
    else:
        ai_summary_text = (
            "No scan history recorded yet. Upload and analyze your first skin lesion to begin tracking your skin health recovery timeline."
        )

    # Chart trend arrays - includes Scan ID and Date/Time timestamp so same-day scans are distinctly formatted
    trend_dates = [f"Scan #{s['id']} ({s['scan_date'][5:16]})" for s in chronological_scans]
    trend_confidences = [s["confidence"] for s in chronological_scans]
    trend_diseases = [s["disease"] for s in chronological_scans]
    trend_ids = [s["id"] for s in chronological_scans]

    # Calculate average confidence
    avg_confidence = 0
    if total_scans > 0:
        avg_confidence = round(sum(s["confidence"] for s in chronological_scans) / total_scans, 1)

    connection.close()

    return render_template(
        "progress.html",
        scans=chronological_scans,
        recent_scans=recent_scans,
        total_scans=total_scans,
        available_diseases=available_diseases,
        selected_disease=selected_disease,
        scan1=scan1,
        scan2=scan2,
        confidence_delta=confidence_delta,
        improvement_percentage=improvement_percentage,
        skin_health_score=skin_health_score,
        health_status=health_status,
        ai_summary_title=ai_summary_title,
        ai_summary_text=ai_summary_text,
        avg_confidence=avg_confidence,
        trend_dates_json=json.dumps(trend_dates),
        trend_confidences_json=json.dumps(trend_confidences),
        trend_diseases_json=json.dumps(trend_diseases),
        trend_ids_json=json.dumps(trend_ids)
    )


@app.route("/history")
def history():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    user_id = session.get("user_id")

    if user_id:
        cursor.execute("""
            SELECT *
            FROM scans
            WHERE user_id = ?
            ORDER BY scan_date DESC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT *
            FROM scans
            WHERE (user_id IS NULL OR user_id = '')
            ORDER BY scan_date DESC
        """)

    scans = cursor.fetchall()

    connection.close()

    return render_template(
        "history.html",
        scans=scans,
        total_scans=len(scans)
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/clear_history", methods=["POST"])
def clear_history():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    user_id = session.get("user_id")

    if user_id:
        cursor.execute("SELECT image FROM scans WHERE user_id = ?", (user_id,))
        scans = cursor.fetchall()
        for scan in scans:
            image_path = os.path.join("static", scan["image"])
            if os.path.isfile(image_path):
                os.remove(image_path)
        cursor.execute("DELETE FROM scans WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT image FROM scans WHERE (user_id IS NULL OR user_id = '')")
        scans = cursor.fetchall()
        for scan in scans:
            image_path = os.path.join("static", scan["image"])
            if os.path.isfile(image_path):
                os.remove(image_path)
        cursor.execute("DELETE FROM scans WHERE (user_id IS NULL OR user_id = '')")

    # If the scans table is now completely empty, reset sqlite_sequence auto increment
    cursor.execute("SELECT COUNT(*) FROM scans")
    if cursor.fetchone()[0] == 0:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='scans'")

    connection.commit()
    connection.close()

    return "", 200

@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return render_template(
            "index.html",
            error="Please upload an image."
        )


    image = request.files["image"]


    if image.filename == "":
        return render_template(
            "index.html",
            error="No image selected."
        )


    allowed_extensions = ["jpg", "jpeg", "png"]


    extension = image.filename.split(".")[-1].lower()


    if extension not in allowed_extensions:
        return render_template(
            "index.html",
            error="Only JPG, JPEG and PNG images are allowed."
        )

    # Validate image data stream with Pillow before saving to disk
    try:
        test_img = Image.open(image.stream)
        test_img.verify()
        image.stream.seek(0)
    except Exception:
        return render_template(
            "index.html",
            error="Invalid image file uploaded."
        )

    # Generate unique UUID filename to prevent collision/overwriting
    unique_filename = f"{uuid.uuid4().hex}.{extension}"

    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )


    image.save(image_path)
    database_image = image_path.replace("\\", "/").replace("static/", "")

    try:

        img = Image.open(image_path)

        img = img.convert("RGB")

        img = img.resize((224,224))


        img_array = np.array(img)

        img_array = np.expand_dims(
            img_array,
            axis=0
        )


        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(
            img_array
        )


        prediction = model.predict(img_array)


        predicted_index = np.argmax(prediction)


        disease = class_names[predicted_index]


        confidence = round(
            float(np.max(prediction))*100,
            2
        )
        
        user_id = session.get("user_id")

        save_scan(
            user_id,
            database_image,
            disease,
            confidence
        )

        info = disease_info[disease]


        return render_template(
            "result.html",
            image_path=image_path,
            image_url="/" + image_path.replace("\\","/"),
            disease=disease,
            confidence=confidence,
            disease_info=info
        )


    except Exception as e:
        if os.path.isfile(image_path):
            os.remove(image_path)
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    app.run(debug=True)