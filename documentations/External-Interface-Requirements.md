# External Interface Requirements - AWS Pentest System

---

## 3. External Interface Requirements

This section specifies requirements that ensure the AWS Pentest System connects properly to external components.

### Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Pentest System                            │
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   FastAPI    │◄────►│   Service    │◄────►│  Repository  │  │
│  │   Backend    │      │    Layer     │      │    Layer     │  │
│  └──────┬───────┘      └──────────────┘      └───────┬──────┘  │
│         │                                              │          │
└─────────┼──────────────────────────────────────────────┼─────────┘
          │                                              │
          ▼                                              ▼
┌─────────────────┐                          ┌──────────────────┐
│  React Frontend │                          │   PostgreSQL DB  │
│  (localhost:5173)│                          │   (User, Env,    │
│                 │                          │   Scan Metadata) │
└─────────────────┘                          └──────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                            │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   AWS API    │  │  Gemini AI   │  │  MongoDB     │         │
│  │  (boto3)     │  │  (Google)    │  │  (Scan Data) │         │
│  │              │  │              │  │              │         │
│  │ • IAM        │  │ • Triage     │  │ • iam_users  │         │
│  │ • S3         │  │ • Analysis   │  │ • iam_roles  │         │
│  │ • Lambda     │  │ • Commands   │  │ • s3_buckets │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3.1. Hardware Interfaces

### **Client-Side Hardware**
- **Desktop/Laptop:** Minimum 4GB RAM, dual-core processor, Windows 10+/macOS 10.13+/Linux 4.x+
- **Mobile Devices:** Any smartphone with modern web browser (Chrome, Firefox, Safari)
- **Browser Requirements:** JavaScript, cookies, HTTPS/TLS 1.2+ support

### **Server-Side Hardware**
- **Backend Server:** Minimum 8GB RAM, quad-core processor, Python 3.13+ support
- **PostgreSQL Server:** Minimum 4GB RAM (users, environments, scan metadata)
- **MongoDB Server:** Minimum 8GB RAM (scan results with nested JSON)

---

## 3.2. Software Interfaces

### **PostgreSQL Database**
- **Version:** PostgreSQL 12+
- **Connection:** SQLAlchemy ORM with connection pooling
- **Security:** SSL/TLS connections, parameterized queries

### **MongoDB Database**
- **Version:** MongoDB 4.4+
- **Purpose:** Store AWS enumeration results (IAM, S3, Lambda)
- **Connection:** PyMongo client with ThreadPoolExecutor for concurrent queries

### **AWS API (boto3)**
- **Purpose:** Enumerate AWS resources (IAM, S3, Lambda)
- **Authentication:** AWS Access Key + Secret Key (encrypted in PostgreSQL)

### **Google Gemini AI API**
- **Purpose:** Multi-stage security analysis and attack path generation
- **Stages:** Triage (temp 0.3), Deep Analysis (temp 0.4), Commands (temp 0.2)

### **FastAPI Backend**
- **Version:** FastAPI 0.100+
- **Dependencies:** SQLAlchemy, PyMongo, Pydantic, python-jose, bcrypt
- **CORS:** Configured for frontend origins

### **React.js Frontend**
- **Version:** React 18+ with Vite
- **UI Framework:** TailwindCSS
- **State Management:** TanStack Query
- **Authentication:** JWT tokens in localStorage
- **Communication:** REST API calls to backend

### **Python Environment**
- **Version:** Python 3.13+
- **Key Libraries:** FastAPI, boto3, google-generativeai, SQLAlchemy, PyMongo, python-jose, bcrypt
- **Execution:** Uvicorn ASGI server with ThreadPoolExecutor for concurrency

---

## 3.3. Communication Interfaces

- **Frontend ↔ Backend:** HTTP/HTTPS RESTful API with JWT authentication
- **Backend ↔ PostgreSQL:** PostgreSQL wire protocol over TCP (port 5432)
- **Backend ↔ MongoDB:** MongoDB wire protocol over TCP (port 27017)
- **Backend ↔ AWS API:** HTTPS with AWS Signature Version 4
- **Backend ↔ Gemini AI:** HTTPS with API key authentication
- **Data Format:** JSON for all API requests/responses

---

## 3.4. Security Interfaces

- **Data in Transit:** TLS 1.2+ for all external communications
- **Data at Rest:** AWS credentials encrypted in PostgreSQL, bcrypt password hashing
- **Authentication:** JWT tokens (HS256, 24-hour expiration)
- **Authorization:** User-level isolation (users access only their own data)
- **CORS Policy:** Whitelisted frontend origins only
