# Face Skin Assessment System (DermaLens)

**College Engineering Mini-Project — Production-Quality Implementation**

---

## 1. Executive Summary & Architecture

The **Face Skin Assessment System** is an end-to-end computer vision and explainable AI system designed to analyze facial skin patterns from multi-view photographs (Front, Left, Right profiles), extract facial regions via MediaPipe landmarking, evaluate visible patterns using an EfficientNet-B0 deep neural network, generate visual saliency explanations via Grad-CAM, and synthesize physiological explanations grounded in curated dermatological literature.

### System Pipeline
```
User
 │
 ├── Front / Left / Right Capture (Live Webcam or High-Res Upload)
 ▼
Image Quality Assessment (Hard Gate: Blur, Brightness, Lighting, Resolution)
 ▼
Face Detection & Mesh Landmarking (MediaPipe BlazeFace + FaceMesh 468 points)
 ▼
Facial Region Extraction (Forehead, Left Cheek, Right Cheek, Nose, Chin)
 ▼
EfficientNet-B0 Visual Pattern Classification (8 Concern Classes, Dataset A)
 ▼
Explainable AI (Grad-CAM Heatmaps & 60/40 Visual Overlays)
 ▼
Curated Knowledge & Scientific Layer ("Why It Can Occur Scientifically")
 ▼
Clinical Citations (AAD, Mayo Clinic, DermNet NZ) & Consultation Guidance
 ▼
Interactive Results Dashboard
```

> **IMPORTANT CLINICAL DISCLAIMER:**
> This system is strictly an informational and educational engineering demonstration. It is **NOT** a medical diagnostic system, medical device, or prescription tool. An image cannot determine the true underlying medical cause of a skin condition.

---

## 2. Machine Learning Architecture & Limitations

### Dataset A Specifics
- **Concern Classes (8 Classes):**
  1. `Redness` (Erythema)
  2. `dark spots` (Hyperpigmentation)
  3. `inflammatory acne` (Papules, Pustules)
  4. `non inflammatory acne black heads` (Open Comedones)
  5. `non inflammatory acne white heads` (Closed Comedones)
  6. `pigmentation` (Uneven Tone / Melasma)
  7. `pores` (Enlarged Follicular Openings)
  8. `wrinkles` (Fine Lines & Expression Folds)
- **Dataset Size:** 4,224 files by class count; 4,222 images processed by training pipeline.
- **Model Checkpoint:** `training/models/efficientnet_b0_skin_concerns.pth`
- **Validation Accuracy:** **92.89%** on the closed Dataset A validation split.
  - *Academic Honesty Note:* This figure represents **validation accuracy on the training split only**. It must **never** be cited as clinical accuracy, real-world accuracy, diagnostic accuracy, or dermatologist-level accuracy.

### Current ML Model Limitations
1. **Single-Label Formulation:** The model predicts the primary visible pattern among the 8 classes. It is not an independently validated multi-label concern detector; multiple skin concerns often coexist.
2. **Region-Level Prototype:** While trained on Dataset A cropped concerns, the prototype applies inference to the 5 facial-region landmark crops. The 92.89% benchmark applies to the split images, not independently validated per-region crops.
3. **Skin Type Module:** Dataset A does not contain validated skin-type ground truth. The system explicitly reports skin-type as **Unavailable** rather than fabricating classifications from brightness or texture heuristics.

---

## 3. Explainable AI (Grad-CAM)

Gradient-weighted Class Activation Mapping (Grad-CAM) generates visual explanations for decisions made by the EfficientNet-B0 classifier:
1. Saliency gradients with respect to the final convolutional block (`model.features[-1]`) are computed during the backward pass.
2. Channel-wise mean pooling calculates importance weights $\alpha_k$.
3. ReLU activation isolates features positively contributing to the target class.
4. The CAM is scaled and overlaid as a JET colormap (40% heatmap + 60% original image) encoded as base64 PNG for the API response.

> **XAI Guardrail:** Grad-CAM illustrates image regions that stimulated the model's prediction. It is an explanation aid, not proof of medical causality or disease pathology.

---

## 4. Curated Dermatological Knowledge Layer

Rather than relying on ungrounded generative AI hallucinations, DermaLens maintains a curated, structured knowledge base in `app/data/skin_concerns_knowledge.py`:
- **Concept Definition & Visual Characteristics**
- **Common Contributing Factors** (UV radiation, sebum dysregulation, genetics, barrier disruption)
- **Why It Can Occur Scientifically** (Vasodilation, melanogenesis, follicular hyperkeratinization)
- **Peer-Reviewed Sources:** American Academy of Dermatology (AAD), Mayo Clinic, DermNet NZ
- **Consultation Guidance:** Clear criteria for when to seek professional dermatologist evaluation.

---

## 5. Security Architecture

1. **Password Hashing:** Argon2id (memory-hard, resistant to GPU/ASIC cracking).
2. **Stateless Authentication:** Signed JWTs using HMAC-SHA256 (`HS256`) with strict expiration.
3. **Ownership Isolation:** User identity is strictly derived from the validated JWT claims—never trusted from frontend payloads.
4. **Input Validation & Quality Gate:** File size limit (10MB), MIME check (JPEG, PNG, WebP), OpenCV image decoding validation, blur and brightness gates.
5. **Private Image Storage:** Images are stored on filesystem (`uploads/`) with random UUIDs; large binary blobs are kept out of MongoDB.
6. **Rate Limiting:** Sliding-window in-memory limiter prevents credential brute-forcing on auth endpoints.

---

## 6. API Reference (`/api/v1`)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/health` | Service and MongoDB Atlas health check | Public |
| `POST` | `/api/v1/auth/register` | Register user with Argon2id hash | Public |
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT | Public |
| `POST` | `/api/v1/auth/logout` | Client token disposal | Public |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Bearer JWT |
| `POST` | `/api/v1/assessments` | Create assessment session | Optional JWT |
| `GET` | `/api/v1/assessments/history` | List assessment history (filtered by user if authenticated) | Optional JWT |
| `GET` | `/api/v1/assessments/{id}` | Retrieve assessment record | Public |
| `DELETE` | `/api/v1/assessments/{id}` | Delete assessment and image records | Ownership |
| `GET` | `/api/v1/assessments/{id}/status` | View status and per-view completion | Public |
| `POST` | `/api/v1/assessments/{id}/images` | Upload image for `front`, `left`, or `right` view | Public |
| `POST` | `/api/v1/assessments/{id}/analyze` | Trigger Grad-CAM and knowledge enrichment | Public |
| `GET` | `/api/v1/assessments/{id}/results` | Fetch complete structured assessment results | Public |
| `GET` | `/api/v1/knowledge` | List all 8 curated concern definitions | Public |
| `GET` | `/api/v1/knowledge/{concept}` | Get detailed knowledge for specific concern | Public |
| `GET` | `/api/v1/sources` | List all scientific and clinical sources | Public |
| `GET` | `/api/v1/sources/{id}` | Get specific clinical source by ID | Public |
| `GET` | `/api/v1/safety` | Retrieve safety disclaimers and model benchmark notes | Public |
| `POST` | `/api/v1/xai/gradcam` | Direct Grad-CAM computation on uploaded image | Public |

---

## 7. Running the System Locally

### Backend (Terminal 1)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```
- API will be accessible at: `http://localhost:8000`
- Interactive Swagger docs at: `http://localhost:8000/docs`
- Built frontend available at: `http://localhost:8000/`

### Frontend Development Server (Terminal 2)
```powershell
cd backend/frontend
npm run dev
```
- Vite dev server with hot reload at: `http://localhost:5173`
- Proxies `/api/*` automatically to backend port 8000.

### Running Test Suite
```powershell
cd backend
.\venv\Scripts\pytest.exe -o pythonpath=. tests/test_api_endpoints.py -v
```
All 5 comprehensive endpoint and lifecycle tests pass with 100% success.
