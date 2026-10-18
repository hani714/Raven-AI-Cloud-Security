<div align="center">

# Raven

**AWS Security Intelligence Platform**

Cloud environments move fast. Security visibility rarely keeps up.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-raven.shoukan--labs.com-blue?style=flat-square)](https://raven.shoukan-labs.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## The problem

Most organizations running on AWS have a reasonable picture of what they've deployed — but a much hazier picture of what's actually exposed. IAM roles accumulate. Misconfigured resources go unnoticed. Privilege escalation paths exist that are genuinely difficult to trace without the right tooling.

On the compliance side, CIS Benchmark checks typically run separately from security assessments: different tools, different timelines, results that rarely connect to the actual attack surface. You end up with two disconnected reports and significant manual effort to make sense of them together.

**Raven closes that gap.**

---

## What it does

Connect your AWS environment, launch a scan, and Raven delivers two things from a single workflow:

- **Offensive security analysis** — IAM enumeration, privilege escalation path mapping, misconfiguration detection, lateral movement opportunities, and proof-of-concept attack paths backed by a GenAI reasoning layer
- **CIS Foundations Benchmark compliance** — automated evaluation against AWS CIS controls, scored and structured, in the same report

No separate tool. No reconciliation effort. One workflow, complete picture.

---

## Features

### Enumeration & reconnaissance
- Deep IAM enumeration — roles, policies, trust relationships, and inline policies
- Multi-service configuration collection across EC2, S3, Lambda, RDS, and more
- Resource relationship mapping for understanding the full blast radius of any exposure

### Attack surface analysis (GenAI-powered)
- Privilege escalation chain detection with mapped attack paths
- Lateral movement opportunity identification
- Misconfiguration prioritization ranked by actual exploitability, not theoretical severity
- Proof-of-concept attack path generation — concrete evidence, not just a risk list

### Compliance evaluation
- Automated AWS CIS Foundations Benchmark assessment
- Per-control pass/fail status with remediation guidance
- Compliance posture correlated directly with offensive findings — same scan, same report

### Reporting
- Structured intelligence reports with attack feasibility scoring
- Risk ratings per finding with mapped CIS control status
- Exportable results for stakeholder review

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite |
| Backend | Python, FastAPI |
| Cloud SDK | boto3 (AWS SDK for Python) |
| AI Layer | Claude / OpenAI API (configurable) |
| Database | PostgreSQL, MongoDB, Neo4j |
| Auth | JWT |

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS credentials
- An Anthropic or OpenAI API key

### 1. Clone the repository

```bash
git clone https://github.com/YarKhan02/Raven.git
cd Raven
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `.env` with your values:

```env
# AWS credentials (or use IAM role / AWS CLI profile)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# AI provider
ANTHROPIC_API_KEY=your_key_here
# or
OPENAI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/raven

# App
SECRET_KEY=your_secret_key
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

Edit `.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

App will be available at `http://localhost:5173`.

---

## Usage

### Running a scan

1. Open the app at `http://localhost:5173`
2. Connect your AWS account using access key credentials or an IAM role ARN
3. Select the scan scope (full account or specific services)
4. Launch the scan — enumeration runs automatically in the background
5. When complete, the GenAI reasoning layer analyzes findings and generates the report
6. Review the **Attack Surface** tab for offensive findings and the **Compliance** tab for CIS results

### Understanding the report

| Section | What it shows |
|---|---|
| Executive summary | Overall risk rating, finding counts by severity |
| Attack paths | Step-by-step privilege escalation chains with feasibility scores |
| Misconfigurations | Ranked list with exploitation likelihood and blast radius |
| Lateral movement | Identified paths between services and roles |
| CIS benchmark | Per-control pass/fail with remediation steps |

---

## Live

A live instance is deployed at **[raven.shoukan-labs.com](https://raven.shoukan-labs.com)**.

---

## Responsible use

Raven is built for **authorized security assessments only**. Only run scans against AWS environments you own or have explicit written permission to test. Unauthorized access to cloud environments is illegal.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built by <a href="https://yarkhan02.github.io">Wali Yar Khan</a>
</div>
