# Azure Deployment Guide — Face Skin Assessment System (DermaLens)

This guide documents deploying the Face Skin Assessment System to **Azure App Service (Linux Containers)** or **Azure Container Apps**, backed by **MongoDB Atlas** and **Azure Blob Storage**.

---

## 1. Prerequisites

1. **Azure CLI** installed (`az --version`) and logged in (`az login`).
2. **Docker Desktop** installed for container image creation.
3. **MongoDB Atlas** cluster with connection URI and network access configured with Azure outbound IP addresses or Private Endpoint (avoiding wildcard `0.0.0.0/0`).
4. **Azure Container Registry (ACR)** or **Docker Hub** account.
5. **Azure Blob Storage Account** for private encrypted storage of assessment biometric images.

---

## 2. Container Image Build & Push

### A. Create an Azure Resource Group and Container Registry (ACR)
```bash
# Set variables
RESOURCE_GROUP="rg-dermalens-prod"
LOCATION="eastus"
ACR_NAME="acrdermalensprod"

# Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
```

### B. Build and Push Container Image
```bash
# Log in to ACR
az acr login --name $ACR_NAME

# Build container image from backend directory
docker build -t $ACR_NAME.azurecr.io/dermalens-api:v1 backend/

# Push image to ACR
docker push $ACR_NAME.azurecr.io/dermalens-api:v1
```

---

## 3. Option A: Deploy to Azure App Service (Recommended)

### A. Create an App Service Plan (B1 or higher for ML memory)
```bash
az appservice plan create \
  --name plan-dermalens \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --is-linux \
  --sku B1
```

### B. Create Web App for Containers
```bash
# Get ACR credentials
ACR_USER=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASS=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Create the Web App with canonical hostname dermalens-backend
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan plan-dermalens \
  --name dermalens-backend \
  --deployment-container-image-name $ACR_NAME.azurecr.io/dermalens-api:v1 \
  --docker-registry-server-user $ACR_USER \
  --docker-registry-server-password $ACR_PASS
```

### C. Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name dermalens-backend \
  --settings \
    MONGODB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority" \
    MONGODB_DATABASE="face_skin_assessment" \
    JWT_SECRET_KEY="<strong-random-production-secret-key-min-32-chars>" \
    ENVIRONMENT="production" \
    CORS_ORIGINS="https://dermalens.vercel.app,https://your-domain.com" \
    AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net" \
    AZURE_STORAGE_CONTAINER="assessment-images" \
    MODEL_PATH="/app/models/efficientnet_b0_skin_concerns.pth" \
    MIN_CONFIDENCE_THRESHOLD="0.35" \
    WEBSITES_PORT="8000"
```

### D. Secure MongoDB Atlas Network Access
Retrieve the dedicated outbound IP addresses assigned to your App Service:
```bash
az webapp show \
  --name dermalens-backend \
  --resource-group $RESOURCE_GROUP \
  --query outboundIpAddresses \
  -o tsv
```
In the MongoDB Atlas Console, navigate to **Network Access** > **IP Access List** and add each outbound IP returned above. Do **NOT** use `0.0.0.0/0` in production.

### E. Verify Deployment
Navigate to `https://dermalens-backend.azurewebsites.net`.
- Frontend loads directly at `/`
- Interactive OpenAPI / Swagger docs at `/docs`
- Health check endpoint at `/api/v1/health`

---

## 4. Vercel Frontend Deployment (Split Architecture)

If deploying the frontend independently on **Vercel** with the backend hosted on **Azure**:
1. Connect your repository to Vercel and configure **Root Directory** to `backend/frontend`.
2. Configure Environment Variable in Vercel project settings:
   `VITE_API_BASE="/api/v1"`
3. The included `backend/frontend/vercel.json` automatically proxies API requests to your Azure App Service:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/v1/:path*",
         "destination": "https://dermalens-backend.azurewebsites.net/api/v1/:path*"
       },
       {
         "source": "/(.*)",
         "destination": "/index.html"
       }
     ]
   }
   ```
4. Add your Vercel deployment domain to `CORS_ORIGINS` in Azure App Service application settings.

---

## 5. Option B: Deploy to Azure Container Apps

```bash
# Create Container Apps Environment
az containerapp env create \
  --name env-dermalens \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy Container App
az containerapp create \
  --name app-dermalens \
  --resource-group $RESOURCE_GROUP \
  --environment env-dermalens \
  --image $ACR_NAME.azurecr.io/dermalens-api:v1 \
  --target-port 8000 \
  --ingress external \
  --cpu 1.0 \
  --memory 2.0Gi \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USER \
  --registry-password $ACR_PASS \
  --env-vars \
    MONGODB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority" \
    MONGODB_DATABASE="face_skin_assessment" \
    JWT_SECRET_KEY="<strong-random-production-secret-key-min-32-chars>" \
    ENVIRONMENT="production" \
    AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net" \
    AZURE_STORAGE_CONTAINER="assessment-images" \
    CORS_ORIGINS="https://dermalens.vercel.app,https://your-domain.com"
```

---

## 6. Security Checklist
- [x] HTTPS enforced automatically by Azure (`.azurewebsites.net`).
- [x] Passwords hashed with Argon2id; passwords never stored or logged in plaintext.
- [x] Session authentication via `HttpOnly`, `SameSite=Lax`, `Secure` cookie (`derma_session`) with dual Bearer token support.
- [x] Grad-CAM neural network inferencing endpoint authenticated with rate limiting.
- [x] Private object storage in Azure Blob with zero local filesystem leakage in production.
- [x] Strict Anti-Caching headers (`Cache-Control: private, no-store, must-revalidate`) on all sensitive biometric/profile routes.
- [x] Monotonic atomic assessment numbering via atomic MongoDB sequences with zero duplicate names across deletions.
- [x] Image quality gate rejects blurry, poorly lit, or invalid images prior to ML processing.
- [x] MediaPipe Face Landmarker / BlazeFace detector enforces single-face constraint.
- [x] Audited physical file deletion report cleans up image artifacts upon assessment deletion.
