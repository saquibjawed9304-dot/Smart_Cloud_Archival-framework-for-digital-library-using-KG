# Smart Cloud Archival Framework

An academic digital-library prototype combining metadata search, a knowledge-graph view, PDF ingestion, and AWS integration points for S3, Textract, Bedrock, and Neptune.

## Current runtime

- FastAPI backend serving the vanilla HTML/CSS/JavaScript dashboard
- CSV fallback for zero-dependency demos
- MySQL schema and seed workflow for local or RDS metadata storage
- Deterministic local graph projection with stable node identifiers
- PDF validation and local `pypdf` extraction
- Opt-in AWS adapters for S3, asynchronous Textract, Claude on Bedrock, and Neptune

AWS services are disabled unless their environment values are configured. The local test suite never needs AWS credentials.

## Run locally with sample data

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn src.backend.main:app --reload
```

Open `http://127.0.0.1:8000`. API documentation is at `http://127.0.0.1:8000/docs`.

The default `DATA_BACKEND=csv` uses `dataset/raw/library_records.csv`, which contains 12 sample records.

## Run with MySQL

Create a database in the existing MySQL installation, copy `.env.example` to `.env`, and set:

```text
DATA_BACKEND=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=smart_archival
MYSQL_USER=root
MYSQL_PASSWORD=your-password
```

Load the schema and sample records:

```powershell
.venv\Scripts\python.exe -c "from src.backend.database import initialize_schema; initialize_schema()"
.venv\Scripts\python.exe scripts\seed_data.py
.venv\Scripts\python.exe -m uvicorn src.backend.main:app --reload
```

The seed script is idempotent and can also be used against an RDS MySQL endpoint after networking and credentials are configured.

## Verification

```powershell
.venv\Scripts\python.exe -m compileall src
.venv\Scripts\python.exe -m pytest -q
```

The tests cover the CSV fallback, search/statistics, typed API responses, frontend serving, graph 404 behavior, and invalid/valid PDF handling.

## AWS handoff

Recommended topology:

```text
Browser -> EC2 / FastAPI -> RDS MySQL
                       -> S3 -> async Textract
                       -> Claude on Bedrock
                       -> Neptune
```

For AWS mode:

1. Place EC2, RDS, and Neptune in the intended VPC and restrict security groups to required application/database ports.
2. Give the EC2 instance role least-privilege access to the S3 bucket, Textract jobs, Bedrock model invocation, and Neptune data APIs.
3. Set `DATA_BACKEND=mysql`, RDS connection settings, `AWS_REGION`, `S3_BUCKET`, `NEPTUNE_ENDPOINT`, and an enabled Bedrock model ID.
4. Run the schema and seed commands against RDS.
5. Configure HTTPS through a reverse proxy or load balancer and set `ALLOWED_ORIGINS` to the real frontend origin.

The AWS adapters are concrete service clients, but real cloud verification remains opt-in because it requires your account resources, model access, VPC routing, and IAM policies.

## Project structure

```text
src/backend/       FastAPI routes, configuration, MySQL schema, data and graph services
src/frontend/      Same-origin dashboard
src/aws/           S3, Textract, Bedrock and Neptune adapters
src/ml_model/      Deterministic extraction fallback
dataset/raw/       Seed CSV records
scripts/           Reproducible database seed command
tests/             Local automated tests
```

## Academic context

The project is developed for Project Phase-I at VIT University, Vellore. The documents in `docs/` contain the supporting report, literature survey, research gap, objectives, and novelty material.
