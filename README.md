# Solarin Ayomide - Digital Twin

AI-powered digital twin representing my skills as a web developer and digital strategist.

## Tech Stack

- **Production web UI:** Vanilla HTML/CSS/JS in `frontend/`; FastAPI in `backend/app/main.py` serves `index.html` and mounts `frontend/static/` at `/static/`. Entry for hosting: `backend/app/main.py` (Vercel / Cloud Run).
- OpenAI GPT-3.5 Turbo
- Python

## Repository layout

| Path | Role |
|------|------|
| `backend/app/` | FastAPI `app`, routes, OpenAI chat, HTML template fill-in (Vercel + `uvicorn` entry). |
| `backend/knowledge/` | Markdown files merged into the system prompt. |
| `frontend/` | `index.html` plus `static/css/styles.css` and `static/js/app.js`. |
| `public/images/` | Gallery thumbnails and `/images/avatar.svg` fallback. |
| `terraform/` | GCP APIs + Artifact Registry (see workflows). |

## Features

- Answers questions about my work experience
- Explains my technical skills
- Discusses collaboration opportunities

## Knowledge base (markdown)

Editable facts for the twin live under `backend/knowledge/` (`*.md`). At startup, `backend/app/main.py` loads every markdown file and appends it to the system prompt. Edit those files and push to `main` to refresh what the model knows; `deploy-app.yml` rebuilds when `backend/**` or `frontend/**` changes.

## Local FastAPI (same app as Cloud Run / Vercel)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Either export the key, or create backend/.env (loaded automatically):
#   echo 'OPENAI_API_KEY=sk-...' > backend/.env
export OPENAI_API_KEY=sk-...
uvicorn backend.app.main:app --reload --port 8000
# open http://127.0.0.1:8000
```

If every reply says the model is not configured, the key is still missing—check the server log for a warning about `OPENAI_API_KEY`.

## Live demo

- **Vercel:** connect the GitHub repo in the Vercel dashboard for automatic deploys from `main`.
- **GCP (rubric — CI + Terraform):** GitHub Actions runs **Terraform** to enable APIs and create an **Artifact Registry** repository, then **builds/pushes** the `Dockerfile` and **deploys Cloud Run**. See **CI/CD & Terraform** below.

## CI/CD & Terraform (course rubric)

This repo satisfies **CI-based deployment (GitHub Actions)** and **infrastructure as code (Terraform)** for GCP.

| Piece | Purpose |
|--------|---------|
| `terraform/` | Declares **enabled APIs** and a **Docker Artifact Registry** repository used by CI. |
| `.github/workflows/deploy-app.yml` | On **push to `main`** (app paths): **Docker build → Artifact Registry → Cloud Run**. |
| `.github/workflows/infra-apply.yml` | **Pull requests** touching `terraform/`: `fmt`, `validate`, `plan`. **`workflow_dispatch`:** `terraform apply` (run this once—or when infra changes—before the first deploy). |

### GitHub repository secrets

Add these in **GitHub → Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `GCP_SA_KEY` | JSON key for a **service account** in your GCP project (see roles below). |
| `GCP_PROJECT_ID` | Plain project ID string (e.g. `jekacode-488803`). |
| `OPENAI_API_KEY` | OpenAI API key used **only in CI** to push a new [Secret Manager](https://cloud.google.com/secret-manager) **version** of `openai-api-key`. Cloud Run **does not** store this value as a plaintext env var; the service mounts the secret at runtime. |

When pasting **`GCP_PROJECT_ID`** (or the OpenAI key), avoid an extra blank line after the value—GitHub stores it verbatim, and a trailing newline used to break Docker image tags. Workflows now strip newlines, but keeping secrets single-line is still best practice.

### Security notes

- **Never commit** API keys or `terraform.tfvars` with secrets; use `backend/.env` locally (gitignored) and GitHub **encrypted** secrets for CI.
- **GCP:** Terraform declares the `openai-api-key` **secret resource** and grants Cloud Run’s default runtime service account **Secret Accessor**. The key material lives only in Secret Manager versions (written by CI or by you with `gcloud`).
- **Vercel:** set `OPENAI_API_KEY` in the Vercel project **Environment Variables** UI (not in the repo). Vercel does not use GCP Secret Manager.
- The app adds standard **security headers** on HTTP responses and validates chat message length server-side. Errors are logged **without** echoing user text or stack traces that could include HTTP credentials.

### Service account roles (bootstrap)

The JSON service account used in `GCP_SA_KEY` needs permission to run Terraform and deploy. For a bootcamp sandbox, **Project → IAM → Grant access** with **Editor** is common; tighter options include combinations of **Service Usage Admin**, **Artifact Registry Administrator**, **Cloud Run Admin**, **Secret Manager** access to add secret versions (`roles/secretmanager.secretVersionAdder` on `openai-api-key` or broader **Secret Manager Admin**), and **Service Account User** on the default compute service account.

### Local Terraform (optional)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars with your project_id
terraform init
terraform plan
terraform apply
```

Do not commit `terraform.tfvars` (it is gitignored).

## Google Cloud Run — step-by-step

These steps deploy the **FastAPI** app in `backend/` (same chat UI as production). The container is defined in the repo root `Dockerfile`.

### 1. Create a Google Cloud project

1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project picker → **New project** → choose a name → **Create**.
3. Note the **Project ID** (for example `my-digital-twin-123`).

### 2. Install and configure the Google Cloud CLI

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`). On macOS, **`brew install --cask google-cloud-sdk`** is often the least fragile option.
2. In a **new** terminal (after `install.sh` or Homebrew), prefer a clean Python for the CLI so your global `pip` packages do not interfere:

```bash
unset PYTHONPATH PYTHONHOME
export PYTHONNOUSERSITE=1
# gcloud 565+ needs Python 3.10+. macOS /usr/bin/python3 is often 3.9 — use Homebrew:
export CLOUDSDK_PYTHON="$(command -v /opt/homebrew/bin/python3 2>/dev/null || command -v /usr/local/bin/python3 2>/dev/null || command -v python3)"
"$CLOUDSDK_PYTHON" -V   # should show 3.10 or newer
```

3. Initialize and sign in:

```bash
gcloud init
```

4. Select the **project** you created when prompted.
5. (Optional) Default region for Cloud Run:

```bash
gcloud config set run/region us-central1
```

#### If `gcloud run deploy` crashes (`packages_distributions`, `unsupported operand type(s) for |`)

`gcloud run deploy` loads libraries that require **Python 3.10+**. Set `CLOUDSDK_PYTHON` as in step 2 above (Homebrew `python3` is the usual fix on Mac).

Also run deploy from the **Digital-twin repository root** (the directory that contains `Dockerfile`), not from `google-cloud-sdk`. Do not type literal `...` in the command; use the full flags from the deploy section below.

#### If `gcloud init` crashes with `oauthlib...resource_owner_password_credentials`

That error usually means either **(A)** the SDK tree under `lib/third_party/oauthlib` is **incomplete** (bad download or extract), or **(B)** Python is picking up a **conflicting** environment.

1. Check that the vendored file exists (adjust the path if your SDK lives elsewhere):

```bash
ls "$HOME/Downloads/google-cloud-sdk/lib/third_party/oauthlib/oauth2/rfc6749/grant_types/resource_owner_password_credentials.py"
```

2. If that file is **missing**, remove any old SDK folder first, then extract again. If you run `tar -xf` and see many **"Could not stat … Not a directory"** lines, an existing `google-cloud-sdk` directory is usually blocking a clean unpack (leftover files vs directories from a bad install):

```bash
cd ~/Downloads
rm -rf google-cloud-sdk
tar -xf google-cloud-cli-darwin-arm.tar.gz
```

(Use `google-cloud-cli-darwin-x86_64.tar.gz` on Intel Macs.) Alternatively extract into an empty folder: `mkdir -p ~/google-cloud-sdk-new && cd ~/google-cloud-sdk-new && tar -xf ~/Downloads/google-cloud-cli-darwin-arm.tar.gz`. Then run `./install.sh` inside the extracted `google-cloud-sdk` directory.

3. If the file **exists**, still run with a clean interpreter and no user site-packages (step 2 above), then:

```bash
gcloud components reinstall
```

4. If it still fails, use **Homebrew** and remove the manual `Downloads` copy from your `PATH` so only one `gcloud` is used:

```bash
brew install --cask google-cloud-sdk
exec zsh -l
gcloud init
```

### 3. Enable the APIs Google needs

Run (replace `YOUR_PROJECT_ID` if you are not already on the right project):

```bash
gcloud services enable run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

- **Cloud Run** — hosts the service.
- **Cloud Build** — builds the container when you use `--source .` or `cloudbuild.yaml`.
- **Artifact Registry** — stores the built image (used automatically with `--source`).
- **Secret Manager** — stores the OpenAI key for Cloud Run (Terraform creates the secret + runtime IAM; you add the **value**).

### 4. OpenAI key in Secret Manager (recommended)

**If you use Terraform from this repo**, `terraform apply` creates an empty secret named **`openai-api-key`** and grants Cloud Run’s default runtime service account permission to read it. You must still add **at least one secret version** (the actual key):

- **Option A — GitHub Actions:** add `OPENAI_API_KEY` to GitHub secrets; each successful deploy runs `gcloud secrets versions add` so Cloud Run always mounts `latest`.
- **Option B — manually** (paste key, **Enter**, then **Ctrl+D** on macOS/Linux to end input):

```bash
gcloud secrets versions add openai-api-key --data-file=-
```

If you **did not** use Terraform and the secret does not exist yet:

```bash
gcloud secrets create openai-api-key --replication-policy=automatic --data-file=-
```

If Terraform later fails with “already exists”, import the existing secret:

```bash
cd terraform
terraform import google_secret_manager_secret.openai_api_key projects/YOUR_PROJECT_ID/secrets/openai-api-key
```

**Manual IAM (only if you skipped Terraform):** grant the default **Compute** service account `roles/secretmanager.secretAccessor` on `openai-api-key` (see earlier README versions or Google’s [Cloud Run secrets](https://cloud.google.com/run/docs/configuring/secrets) guide).

### 5. Deploy from this repository (simplest path)

From the **repository root** (where `Dockerfile` lives):

```bash
cd /path/to/Digital-twin

gcloud run deploy digital-twin \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```

- **`digital-twin`** — Cloud Run service name (change if you like).
- **`--source .`** — Cloud Build builds the `Dockerfile` in the current directory; you do not need Docker installed locally.
- **`--allow-unauthenticated`** — anyone can open the URL (typical for a public portfolio demo). Omit it if you want IAM-only access.

When the command finishes, it prints the **service URL**. Open it in a browser and try the chat.

### 6. Redeploy after code changes

Run the same `gcloud run deploy ...` command again from the repo root (with `--source .`). Cloud Build rebuilds the image and Cloud Run rolls out the new revision.

### 7. Optional: build with `cloudbuild.yaml` then deploy by image

From the repo root:

```bash
gcloud builds submit --config cloudbuild.yaml
```

Then deploy the image Cloud Build pushed (replace `YOUR_PROJECT_ID`):

```bash
gcloud run deploy digital-twin \
  --image gcr.io/YOUR_PROJECT_ID/digital-twin:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```

### 8. Custom domain (optional)

In Cloud Console: **Cloud Run** → your service → **Manage custom domains** and follow the wizard (DNS at your registrar).

### Notes

- The app listens on the **`PORT`** environment variable; Cloud Run sets this automatically. The `Dockerfile` already uses it.
- **Billing:** Cloud Run has a generous free tier; enable billing on the project if Google asks (required for some features).

---

**Built for Andela AI Engineering Bootcamp**
