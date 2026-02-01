print("🔥 app.py started")

from flask import Flask, request, render_template, send_file
import joblib
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# -----------------------------
# Base Directory
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# Load Model, Features, Encoder
# -----------------------------
FEATURE_PATH = os.path.join(BASE_DIR, "analysis", "model", "features.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "analysis", "model", "model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "analysis", "model", "label_encoder.pkl")

feature_names = joblib.load(FEATURE_PATH)
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# -----------------------------
# Upload Folder
# -----------------------------
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PREDICTION_FILE = os.path.join(UPLOAD_FOLDER, "predictions.csv")

# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------
# Upload & Predict (Chunk-Based)
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")

    if not file:
        return render_template("index.html", error="Please upload a CSV file.")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        chunk_size = 50_000   # adjust based on RAM
        preview_rows = []
        summary = {}

        # Remove old prediction file if exists
        if os.path.exists(PREDICTION_FILE):
            os.remove(PREDICTION_FILE)

        # Process CSV in chunks
        for i, chunk in enumerate(pd.read_csv(filepath, chunksize=chunk_size)):

            # Ensure all required features exist
            for col in feature_names:
                if col not in chunk.columns:
                    chunk[col] = 0

            X = chunk[feature_names]

            # Clean data
            X = X.apply(pd.to_numeric, errors="coerce")
            X.replace([np.inf, -np.inf], np.nan, inplace=True)
            X.fillna(0, inplace=True)
            X = X.clip(-1e6, 1e6).astype(np.float32)

            # Predict
            preds = model.predict(X)
            attack_types = label_encoder.inverse_transform(preds)

            result_chunk = pd.DataFrame({
                "Attack Type": attack_types
            })

            # Save output incrementally
            if i == 0:
                result_chunk.to_csv(PREDICTION_FILE, index=False)
            else:
                result_chunk.to_csv(
                    PREDICTION_FILE,
                    mode="a",
                    header=False,
                    index=False
                )

            # Collect preview (first ~100 rows total)
            if len(preview_rows) < 100:
                preview_rows.append(result_chunk)

            # Update summary
            for attack in attack_types:
                summary[attack] = summary.get(attack, 0) + 1

        preview_df = pd.concat(preview_rows).head(100)

        # Headline attack (ignore BENIGN if others exist)
        non_benign = {k: v for k, v in summary.items() if k != "BENIGN"}
        headline_attack = max(non_benign, key=non_benign.get) if non_benign else "BENIGN"

        return render_template(
            "index.html",
            success="Prediction completed successfully",
            headline_attack=headline_attack,
            summary=summary,
            table=preview_df.to_html(
                classes="table table-dark table-striped",
                index=False
            ),
            download_ready=True
        )

    except Exception as e:
        return render_template("index.html", error=str(e))

# -----------------------------
# Download Full Prediction CSV
# -----------------------------
@app.route("/download")
def download_predictions():
    if not os.path.exists(PREDICTION_FILE):
        return "Prediction file not found. Please upload and predict first."

    return send_file(
        PREDICTION_FILE,
        as_attachment=True,
        download_name="cyber_threat_predictions.csv"
    )

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
