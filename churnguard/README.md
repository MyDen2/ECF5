# ChurnGuard API

API de prédiction de churn client basée sur un modèle de machine learning, déployée avec **FastAPI**, **MLflow** et **Docker**.

---

## CI/CD

![CI](https://github.com/MyDen2/ECF5/actions/workflows/ci.yml/badge.svg)

* ✔ CI : build + scan sécurité avec Trivy
* ✔ CD : build & push image Docker sur GHCR
* ✔ Release automatique via tags (`v*.*.*`)
* ✔ Changelog généré avec Conventional Commits (git-cliff)

## Architecture

```
                    ┌──────────────┐
                    │   Trainer    │
                    └──────┬───────┘
                           │ log modèle, métriques, paramètres
                           v
┌──────────────┐    ┌──────────────────────┐
│ Client curl  │ -> │     FastAPI API       │
└──────────────┘    └──────────┬───────────┘
                               │ charge le modèle
                               v
                    ┌──────────────────────┐
                    │ MLflow Tracking /    │
                    │ Model Registry       │
                    └──────────┬───────────┘
                               │ stocke
                               v
                    ┌──────────────────────┐
                    │ Artefact modèle      │
                    └──────────────────────┘
```
## Structure du projet

```text
ECF5/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── churnguard/
│   ├── api/
│   │   └── main.py
│   ├── churnguard/
│   │   ├── __init__.py
│   │   ├── data.py
│   │   ├── evaluate.py
│   │   └── train.py
|   |── data/
│   |   └── telco_churn.csv
│   ├── tests/
│   │   ├── test_data.py
│   │   └── test_train.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── pyproject.toml
│   ├── poetry.lock
│   └── README.md
├── mlops-churnguard/ # élément de départ non touché
│   └── repo-depart/ 
├── .pre-commit-config.yaml
├── .gitignore
├── sujet.md
└── cliff.toml
```

## Quickstart

```bash
git clone https://github.com/MyDen2/ECF5.git
cd ECF5

docker compose up --build
```

Toute la stack démarre en moins de 2 minutes :

* API → http://localhost:8000
* MLflow → http://localhost:5000



## Test de l’API

### Health check

```bash
curl http://localhost:8000/health
```

Exemple de réponse :

```json
{
  "status": "ok",
  "model": "churnguard",
  "version": "..."
}
```

### Prédiction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender":"Female",
    "SeniorCitizen":0,
    "Partner":"Yes",
    "Dependents":"No",
    "tenure":1,
    "PhoneService":"No",
    "MultipleLines":"No phone service",
    "InternetService":"DSL",
    "OnlineSecurity":"No",
    "OnlineBackup":"Yes",
    "DeviceProtection":"No",
    "TechSupport":"No",
    "StreamingTV":"No",
    "StreamingMovies":"No",
    "Contract":"Month-to-month",
    "PaperlessBilling":"Yes",
    "PaymentMethod":"Electronic check",
    "MonthlyCharges":29.85,
    "TotalCharges":29.85
  }'
```

Exemple de réponse :

```json
{
  "prediction": 0,
  "probability": 0.23
}
```

### Prédictions multiples

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '[
    {
      "gender":"Female",
      "SeniorCitizen":0,
      "Partner":"Yes",
      "Dependents":"No",
      "tenure":1,
      "PhoneService":"No",
      "MultipleLines":"No phone service",
      "InternetService":"DSL",
      "OnlineSecurity":"No",
      "OnlineBackup":"Yes",
      "DeviceProtection":"No",
      "TechSupport":"No",
      "StreamingTV":"No",
      "StreamingMovies":"No",
      "Contract":"Month-to-month",
      "PaperlessBilling":"Yes",
      "PaymentMethod":"Electronic check",
      "MonthlyCharges":29.85,
      "TotalCharges":29.85
    },
    {
      "gender":"Male",
      "SeniorCitizen":1,
      "Partner":"No",
      "Dependents":"No",
      "tenure":10,
      "PhoneService":"Yes",
      "MultipleLines":"Yes",
      "InternetService":"Fiber optic",
      "OnlineSecurity":"No",
      "OnlineBackup":"No",
      "DeviceProtection":"Yes",
      "TechSupport":"No",
      "StreamingTV":"Yes",
      "StreamingMovies":"Yes",
      "Contract":"Month-to-month",
      "PaperlessBilling":"Yes",
      "PaymentMethod":"Credit card (automatic)",
      "MonthlyCharges":89.10,
      "TotalCharges":891.00
    }
  ]'
```

Exemple de réponse :

```json
[
  {"prediction": 0, "probability": 0.23},
  {"prediction": 1, "probability": 0.78}
]
```

## Image Docker

Image disponible sur GitHub Container Registry :

```
ghcr.io/<TON_USER>/churnguard:v0.1.0
```

## Stack technique

* 🐍 Python 3.11
* ⚡ FastAPI
* 📊 MLflow
* 🐳 Docker / Docker Compose
* 🔐 Trivy (scan sécurité)
* 🔁 GitHub Actions (CI/CD)

## Workflow CI/CD

### CI (Continuous Integration)

* Build Docker
* Scan vulnérabilités avec Trivy
* Échec si vulnérabilités **critiques**

### CD (Continuous Deployment)

* Déclenché sur tag (`v*.*.*`)
* Build image Docker
* Push vers GHCR
* Création d’une release GitHub automatique

---

## Changelog

Généré automatiquement avec **Conventional Commits** via git-cliff.

## Bonus implémentés

- Healthcheck Docker configuré sur l’API.
- Utilisation de `depends_on.condition: service_healthy` dans Docker Compose.
- Image Docker multi-stage.
- Utilisateur non-root dans l’image runtime.
- Scan Trivy dans le workflow CI.
- Release notes générées automatiquement avec git-cliff.