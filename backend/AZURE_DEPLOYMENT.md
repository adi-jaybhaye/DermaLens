# Azure Deployment Guide — Face Skin Assessment System (DermaLens)

This guide documents deploying the Face Skin Assessment System to **Azure App Service (Linux Containers)** or **Azure Container Apps**, backed by **MongoDB Atlas**.

---

## 1. Prerequisites

1. **Azure CLI** installed (`az --version`) and logged in (`az login`).
2. **Docker Desktop** installed for container image creation.
3. **MongoDB Atlas** cluster with connection URI and network whitelist configured (allowing Azure IP ranges or `0.0.0.0/0`).
4. **Azure Container Registry (ACR)** or **Docker Hub** account.

---

## 2. Container Image Build & Push

### A. Create an Azure Resource Group and Container Registry (ACR)
```bash
# Set variables
RESOURCE_GROUP="rg-dermlens-prod"
LOCATION="eastus"
ACR_NAME="acrdermlensprod"

# Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
```

### B. Build and Push Container Image
```bash
# Log in to ACR
az acr login --name $ACR_NAME

# Build container image with multi-stage frontend + backend
docker build -t $ACR_NAME.azurecr.io/dermlens-api:v1 .

# Push image to ACR
docker push $ACR_NAME.azurecr.io/dermlens-api:v1
```

---

## 3. Option A: Deploy to Azure App Service (Recommended)

### A. Create an App Service Plan (B1 or higher for ML memory)
```bash
az appservice plan create \
  --name plan-dermlens \
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

# Create the Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan plan-dermlens \
  --name dermlens-assessment-app \
  --deployment-container-image-name $ACR_NAME.azurecr.io/dermlens-api:v1 \
  --docker-registry-server-user $ACR_USER \
  --docker-registry-server-password $ACR_PASS
```

### C. Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name dermlens-assessment-app \
  --settings \
    MONGODB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority" \
    MONGODB_DATABASE="face_skin_assessment" \
    JWT_SECRET_KEY="<strong-random-production-secret-key>" \
    ENVIRONMENT="production" \
    WEBSITES_PORT="8000"
```

### D. Verify Deployment
Navigate to `https://dermlens-assessment-app.azurewebsites.net`.
- Frontend loads directly at `/`
- Interactive Swagger docs at `/docs`
- Health check endpoint at `/api/v1/health`

---

## 4. Option B: Deploy to Azure Container Apps

```bash
# Create Container Apps Environment
az containerapp env create \
  --name env-dermlens \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Deploy Container App
az containerapp create \
  --name app-dermlens \
  --resource-group $RESOURCE_GROUP \
  --environment env-dermlens \
  --image $ACR_NAME.azurecr.io/dermlens-api:v1 \
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
    JWT_SECRET_KEY="<strong-random-production-secret-key>" \
    ENVIRONMENT="production"
```

---

## 5. Security Checklist
- [x] HTTPS enforced automatically by Azure (`.azurewebsites.net`).
- [x] Passwords hashed with Argon2id; passwords never stored or logged in plaintext.
- [x] MongoDB Atlas credentials restricted to environment configuration.
- [x] JWT tokens signed with HMAC-SHA256 (`HS256`) and expiration claims.
- [x] In-memory rate limiting active on `/api/v1/auth/*` endpoints.
- [x] Image quality gate rejects invalid images prior to ML processing.
