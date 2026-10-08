# College Mini-Project Demo Walkthrough Script

Use this script during your project presentation or lab viva to demonstrate all components of the **Face Skin Assessment System**.

---

## Step 1: System Overview & Academic Integrity (2 Minutes)
1. **Open Swagger Docs & Dashboard:**
   - Navigate to `http://localhost:8000/docs` to demonstrate the clean FastAPI OpenAPI structure (`/api/v1/...`).
   - Navigate to `http://localhost:8000/` to demonstrate the modern, gender-neutral skincare UI (ivory/cream/terracotta aesthetic).
2. **Key Talking Points:**
   - Built on **FastAPI**, **PyTorch (EfficientNet-B0)**, **MediaPipe (468 landmarks)**, and **MongoDB Atlas**.
   - Emphasize academic honesty: "The model was trained on Dataset A containing 8 concern classes and achieved 92.89% validation split accuracy. We clearly declare this as an educational prototype, not clinical or diagnostic accuracy."
   - Explain why skin type is reported as **Unavailable**: "Rather than inventing fake heuristic metrics from brightness, our system adheres to scientific principles and reports skin-type unavailable until a validated labeled dataset is provided."

---

## Step 2: Multi-View Capture & Preparation Protocol (2 Minutes)
1. Click **"Start Skin Assessment"**.
2. Show the **Preparation Protocol**:
   - Natural diffuse lighting, neutral expression, clean surface, 40-50 cm distance.
3. Advance to **Multi-View Capture**:
   - Demonstrate the 3 angles: **Front**, **Left Profile (45°)**, and **Right Profile (45°)**.
   - Demonstrate the dual input modes: **Live Webcam snapshot** OR **High-resolution image upload**.
   - Show how the thumbnail preview lets users review or retake each view independently.

---

## Step 3: Hard Image Quality Gate Demonstration (1 Minute)
1. Explain the quality check mechanism (`app/ml/quality/image_quality.py`):
   - Calculates Laplacian variance for blur.
   - Computes grayscale mean brightness for under/overexposure.
   - Checks image resolution thresholds.
2. If an image is dark, blurry, or lacks a face, the system halts before ML inference and delivers structured feedback asking for recapture.

---

## Step 4: ML Inference & 5-Region Landmarking (2 Minutes)
1. Submit the 3 views.
2. Show the animated processing stepper:
   - MediaPipe detects the face and extracts 468 landmark points.
   - 5 anatomical regions are extracted: **Forehead**, **Left Cheek**, **Right Cheek**, **Nose**, and **Chin**.
   - Region crops are fed into EfficientNet-B0 to predict visible concern probabilities.

---

## Step 5: Explainable AI (Grad-CAM) Visualizer (3 Minutes)
1. On the Results Dashboard, select any region (e.g., *Forehead* or *Cheek*).
2. Point out the **Grad-CAM Visualizer**:
   - Toggle between **Heatmap Overlay** (60% image + 40% JET colormap) and **Heatmap** alone.
   - Show how the model highlights the salient pixel clusters (e.g., hyperpigmented spots or erythema) that stimulated its classification.
3. State the XAI disclaimer clearly:
   - "Grad-CAM explains the neural network's visual attention; it does not claim biological causality or medical diagnosis."

---

## Step 6: Curated Dermatological Knowledge & Citations (2 Minutes)
1. Scroll to the **Understanding the Concern** card:
   - Review **"Why Did the AI Flag This?"** (observable pattern description).
   - Review **"Why It Can Occur Scientifically?"** (physiological mechanisms such as vasodilation, melanogenesis, or follicular hyperkeratinization).
   - Review the clickable citations to **American Academy of Dermatology (AAD)**, **Mayo Clinic**, and **DermNet NZ**.
2. Review the **Consultation Guidance**:
   - When users should see an in-person board-certified dermatologist.

---

## Step 7: Security & Backend Architecture (2 Minutes)
1. Demonstrate User Authentication:
   - Register a new account (`/api/v1/auth/register`) or sign in (`/api/v1/auth/login`).
   - Passwords hashed using **Argon2id** (memory-hard algorithm).
   - Stateless **Bearer JWT** authorization header.
   - Private assessments history isolated per authenticated user identity.
2. Point out that images are saved with random UUIDs in private filesystem storage rather than clogging MongoDB Atlas with heavy binary blobs.

---

## Step 8: Automated Test Verification (1 Minute)
Run the test suite in terminal:
```bash
pytest -o pythonpath=. tests/test_api_endpoints.py -v
```
Show examiners that all health, auth, knowledge, sources, and assessment lifecycle tests pass with 100% green exit code 0.
