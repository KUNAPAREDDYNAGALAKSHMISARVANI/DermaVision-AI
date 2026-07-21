import os
import numpy as np
import tensorflow as tf

from database import save_scan
from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file


app = Flask(__name__)


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

    import sqlite3

    connection = sqlite3.connect("database/dermavision.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # -------------------------------
    # Total scans
    # -------------------------------
    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]

    # -------------------------------
    # Average confidence
    # -------------------------------
    cursor.execute("SELECT AVG(confidence) FROM scans")
    avg_confidence = cursor.fetchone()[0]

    if avg_confidence is None:
        avg_confidence = 0

    avg_confidence = round(avg_confidence, 2)

    # -------------------------------
    # Latest Scan
    # -------------------------------
    cursor.execute("""
        SELECT *
        FROM scans
        ORDER BY scan_date DESC
        LIMIT 1
    """)

    latest_scan = cursor.fetchone()

    # -------------------------------
    # Recent scans
    # -------------------------------
    cursor.execute("""
        SELECT *
        FROM scans
        ORDER BY scan_date DESC
        LIMIT 5
    """)

    recent_scans = cursor.fetchall()

    # -------------------------------
    # Disease Distribution
    # -------------------------------
    cursor.execute("""

        SELECT disease,
               COUNT(*) as total

        FROM scans

        GROUP BY disease

    """)

    disease_rows = cursor.fetchall()

    disease_labels = []
    disease_counts = []

    for row in disease_rows:

        disease_labels.append(row["disease"])
        disease_counts.append(row["total"])

    # -------------------------------
    # Average Confidence Per Disease
    # -------------------------------
    cursor.execute("""

        SELECT
            disease,
            ROUND(AVG(confidence),2) AS avg_confidence

        FROM scans

        GROUP BY disease

        ORDER BY avg_confidence DESC

    """)

    confidence_rows = cursor.fetchall()
    confidence_labels = []
    confidence_values = []

    for row in confidence_rows:
        confidence_labels.append(row["disease"])
        confidence_values.append(row["avg_confidence"])

    connection.close()
    
    # -------------------------------
    # Dynamic Health Tip
    # -------------------------------

    health_tip = {
        "title": "Healthy Skin Tips",
        "message": "Protect your skin by following a healthy skincare routine."
    }

    if latest_scan:
        disease = latest_scan["disease"]

        tips = {
            "Actinic keratosis": {
                "title": "☀ Sun Protection",
                "message": "Avoid prolonged sun exposure, wear protective clothing, and use SPF 30+ sunscreen daily."
            },
            "Atopic Dermatitis": {
                "title": "💧 Moisturize Frequently",
                "message": "Use fragrance-free moisturizers, avoid harsh soaps, and keep your skin hydrated."
            },
            "Benign keratosis": {
                "title": "🔍 Monitor Your Skin",
                "message": "Observe any changes in size, color, or shape and consult a dermatologist if needed."
            },
            "Dermatofibroma": {
                "title": "🩹 Avoid Irritation",
                "message": "Do not scratch or injure the affected area. Seek medical advice if it becomes painful."
            },
            "Melanocytic nevus": {
                "title": "🧴 Skin Self-Examination",
                "message": "Regularly check your moles using the ABCDE rule and protect yourself from UV exposure."
            },
            "Melanoma": {
                "title": "⚠ Immediate Medical Attention",
                "message": "Consult a dermatologist as soon as possible. Early diagnosis greatly improves treatment success."
            },
            "Squamous cell carcinoma": {
                "title": "☀ Limit UV Exposure",
                "message": "Wear sunscreen and schedule a dermatologist appointment for proper evaluation."
            },
            "Tinea Ringworm Candidiasis": {
                "title": "🧼 Maintain Hygiene",
                "message": "Keep the affected area clean and dry, avoid sharing towels, and complete antifungal treatment."
            },
            "Vascular lesion": {
                "title": "❤️ Observe Skin Changes",
                "message": "Monitor any changes in color, size, or bleeding and consult a dermatologist if changes occur."
            }
        }

        health_tip = tips.get(disease, health_tip)

    return render_template(
        "dashboard.html",
        total_scans=total_scans,
        avg_confidence=avg_confidence,
        latest_scan=latest_scan,
        recent_scans=recent_scans,
        disease_labels=disease_labels,
        disease_counts=disease_counts,
        confidence_labels=confidence_labels,
        confidence_values=confidence_values,
        health_tip=health_tip
    )


@app.route("/report/<int:scan_id>")
def report(scan_id):

    import sqlite3

    connection = sqlite3.connect("database/dermavision.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""

        SELECT *

        FROM scans

        WHERE id=?

    """, (scan_id,))

    scan = cursor.fetchone()

    connection.close()

    if scan is None:

        return "Report not found."

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

    import sqlite3

    connection = sqlite3.connect("database/dermavision.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM scans WHERE id=?",
        (scan_id,)
    )

    scan = cursor.fetchone()

    connection.close()

    if scan is None:
        return "Report not found."

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

    import sqlite3

    connection = sqlite3.connect("database/dermavision.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT image FROM scans WHERE id=?",
        (scan_id,)
    )

    scan = cursor.fetchone()

    if scan:

        image_path = os.path.join("static", scan["image"])

        if os.path.exists(image_path):
            os.remove(image_path)

        cursor.execute(
            "DELETE FROM scans WHERE id=?",
            (scan_id,)
        )

        connection.commit()

    connection.close()

    return redirect(url_for("history"))

@app.route("/history")
def history():

    import sqlite3

    connection = sqlite3.connect("database/dermavision.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM scans
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

    import sqlite3

    connection = sqlite3.connect("database/dermavision.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Get all image paths
    cursor.execute("SELECT image FROM scans")
    scans = cursor.fetchall()

    # Delete uploaded images
    for scan in scans:

        image_path = os.path.join("static", scan["image"])

        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete all scan records
    cursor.execute("DELETE FROM scans")

    # Reset auto increment
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


    image_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        image.filename
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
        
        save_scan(
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
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    app.run(debug=True)