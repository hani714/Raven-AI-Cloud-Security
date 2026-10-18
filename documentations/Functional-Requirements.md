# Functional Requirements - AWS Pentest System

## 4. Functional Requirements

### 4.1. Functional Hierarchy

#### 1. User Management
- 1.1 Register Security Analysts
- 1.2 Login / Authentication
- 1.3 Manage User Profiles
- 1.4 Logout / Session Termination

#### 2. AWS Environment Management
- 2.1 Create AWS Environment
- 2.2 View All Environments
- 2.3 Delete Environment
- 2.4 Validate AWS Credentials

#### 3. Security Scanning Functionality
- 3.1 Create Security Scans
- 3.2 Run AWS Resource Enumeration
  - 3.2.1 IAM Enumeration (Users, Roles, Groups, Policies)
  - 3.2.2 S3 Enumeration (Buckets, Permissions, Encryption)
  - 3.2.3 Lambda Enumeration (Functions, Layers, Configurations)
- 3.3 View Scan History
- 3.4 View Detailed Scan Results

#### 4. AI-Powered Attack Path Analysis Module
- 4.1 Preprocess Enumeration Data
- 4.2 Perform Security Risk Analysis
- 4.3 Generate Attack Paths with Multi-Stage LLM
  - 4.3.1 Stage 1: Quick Triage
  - 4.3.2 Stage 2: Deep Security Analysis
  - 4.3.3 Stage 3: AWS CLI Command Generation
- 4.4 Display Results and Recommendations

#### 5. Prompt Management & LLM Integration
- 5.1 Load Prompt Templates
- 5.2 Construct Dynamic Prompts
- 5.3 Handle LLM Responses

#### 6. Database & Storage Management
- 6.1 PostgreSQL Operations (Users, Environments, Scan Metadata)
- 6.2 MongoDB Operations (IAM, S3, Lambda Results)

#### 7. System Management & Infrastructure
- 7.1 API Request Handling
- 7.2 External Service Communication (AWS API, Gemini AI)
- 7.3 Security & Privacy (JWT, Encryption, Authorization)
- 7.4 Error Handling & Validation
