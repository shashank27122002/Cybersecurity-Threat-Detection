Cybersecurity Threat Detection System

A Machine Learning–powered web application that detects and classifies cybersecurity threats from network traffic data using a trained Random Forest model.
Built with Python, Flask, Scikit-learn, and Bootstrap UI.

📌 Project Overview

This project analyzes network traffic CSV files (e.g. CIC-IDS dataset format) and predicts whether traffic is:

BENIGN

DoS Attack

Port Scan

Brute Force

Web Attack

(extendable to more attack types)

The system is optimized to handle very large CSV files efficiently using chunk-based prediction, avoiding memory overflow.

🧠 Machine Learning Details

Algorithm: Random Forest Classifier

Framework: Scikit-learn

Training: Done in analysis.ipynb

Target Variable: Label

Label Encoding: Stored using LabelEncoder

Saved Artifacts:

model.pkl

features.pkl

label_encoder.pkl

⚠️ During inference, the uploaded CSV does NOT need the Label column.
The model predicts attack types purely from traffic features.

How to Run Locally
1️⃣ Clone the repository
git clone https://github.com/shashanknb27122002/Cybersecurity-Threat-Detection.git
cd Cybersecurity-Threat-Detection


2️⃣ Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the app
python app.py