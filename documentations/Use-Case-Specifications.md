# Use Case Specifications - AWS Pentest System

---

## **<UC-AUTH-01>**

| Use case Id: | UC-AUTH-01 |
|--------------|------------|
| **Actors:** | Security Analyst: Initiates registration |
| **Feature:** | User Registration |
| **Pre-condition:** | User must have valid email address. System database must be operational. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst navigates to registration page. | System displays registration form with email and password fields. |
| **2.** | Security Analyst enters email, password, and confirm password. | System validates input format. |
| **3.** | Security Analyst clicks "Register." | System hashes password, creates user account, stores in PostgreSQL database, and displays success message. |

**Alternate Scenarios:**
- **1a: If email already exists, system displays error: "Email already registered."**
- **2a: If password and confirm password don't match, system displays error: "Passwords do not match."**
- **3a: If email format is invalid, system displays error: "Invalid email format."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | New user account created and stored in database. |
| | User can now log in with credentials. |

### **Use Case Cross referenced**

- **UC-AUTH-02:** Security Analyst logs in after registration.

---

## **<UC-AUTH-02>**

| Use case Id: | UC-AUTH-02 |
|--------------|------------|
| **Actors:** | Security Analyst: Initiates login |
| **Feature:** | User Authentication |
| **Pre-condition:** | User must have registered account. PostgreSQL database must be operational. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst navigates to login page. | System displays login form with email and password fields. |
| **2.** | Security Analyst enters email and password. | System validates credentials against database. |
| **3.** | Security Analyst clicks "Login." | System verifies password hash, generates JWT access token, and returns token with user data. |
| **4.** | System stores JWT token in client. | User is redirected to dashboard. |

**Alternate Scenarios:**
- **2a: If email not found, system displays error: "Incorrect email or password" (401 Unauthorized).**
- **2b: If password incorrect, system displays error: "Incorrect email or password" (401 Unauthorized).**
- **3a: If database connection fails, system displays error: "Service temporarily unavailable."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | User authenticated with valid JWT token. |
| | User session established for subsequent API calls. |

### **Use Case Cross referenced**

- **UC-ENV-01:** After login, user can create environments.
- **UC-SCAN-01:** After login, user can create scans.

---

## **<UC-ENV-01>**

| Use case Id: | UC-ENV-01 |
|--------------|------------|
| **Actors:** | Security Analyst: Creates AWS environment configuration |
| **Feature:** | Create AWS Environment |
| **Pre-condition:** | User must be logged in with valid JWT token. User must have AWS access credentials (access key, secret key, region). |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst selects "Create Environment" from dashboard. | System displays environment creation form. |
| **2.** | Security Analyst enters environment name, AWS access key, secret key, and region. | System validates input format. |
| **3.** | Security Analyst clicks "Create." | System encrypts credentials, stores environment in PostgreSQL with user_id association, and displays success message. |

**Alternate Scenarios:**
- **2a: If required fields are missing, system displays error: "All fields are required."**
- **3a: If AWS credentials are invalid format, system displays validation error.**
- **3b: If database error occurs, system displays error: "Failed to create environment."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | AWS environment configuration stored in database. |
| | Environment available for scan creation. |

### **Use Case Cross referenced**

- **UC-ENV-02:** User can view all created environments.
- **UC-ENV-03:** User can delete environment.
- **UC-SCAN-01:** Environment required to create scan.

---

## **<UC-ENV-02>**

| Use case Id: | UC-ENV-02 |
|--------------|------------|
| **Actors:** | Security Analyst: Views environment list |
| **Feature:** | List AWS Environments |
| **Pre-condition:** | User must be logged in. At least one environment must exist. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst navigates to environments page. | System queries PostgreSQL for user's environments ordered by created_at DESC. |
| **2.** | System retrieves environments. | Displays list with environment name, region, and creation date. |

**Alternate Scenarios:**
- **2a: If no environments exist, system displays message: "No environments found. Create your first environment."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | User views all their AWS environments. |

### **Use Case Cross referenced**

- **UC-ENV-01:** Create Environment adds to this list.
- **UC-ENV-03:** Delete Environment removes from this list.

---

## **<UC-ENV-03>**

| Use case Id: | UC-ENV-03 |
|--------------|------------|
| **Actors:** | Security Analyst: Deletes AWS environment |
| **Feature:** | Delete AWS Environment |
| **Pre-condition:** | User must be logged in. Environment must exist and belong to user. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst selects environment from list. | System displays environment details with delete option. |
| **2.** | Security Analyst clicks "Delete." | System displays confirmation dialog. |
| **3.** | Security Analyst confirms deletion. | System removes environment from PostgreSQL database and displays success message. |

**Alternate Scenarios:**
- **1a: If environment not found or unauthorized, system displays error: "Environment not found" (404).**
- **3a: If environment has associated scans, system may display warning or prevent deletion (based on business rules).**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Environment deleted from database. |
| | Environment no longer appears in list. |

### **Use Case Cross referenced**

- **UC-ENV-02:** Deleted environment removed from list.

---

## **<UC-SCAN-01>**

| Use case Id: | UC-SCAN-01 |
|--------------|------------|
| **Actors:** | Security Analyst: Creates security scan |
| **Feature:** | Create AWS Security Scan |
| **Pre-condition:** | User must be logged in. At least one environment must exist. AWS credentials must be valid. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst selects "Create Scan" from dashboard. | System displays scan creation form with environment dropdown. |
| **2.** | Security Analyst selects target environment. | System validates environment belongs to user. |
| **3.** | Security Analyst clicks "Start Scan." | System initiates enumeration process (UC-SCAN-04). |
| **4.** | System runs AWS enumeration in background. | Displays loading indicator and progress updates. |
| **5.** | Enumeration completes. | System stores scan metadata in PostgreSQL, stores results in MongoDB, and displays completion message. |

**Alternate Scenarios:**
- **2a: If environment invalid or unauthorized, system displays error: "Invalid environment or unauthorized access."**
- **4a: If AWS credentials expired/invalid, system displays error: "AWS authentication failed."**
- **4b: If AWS API rate limit exceeded, system retries with exponential backoff.**
- **5a: If enumeration fails, system logs error and displays: "Scan failed. Check AWS credentials and permissions."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Scan record created in PostgreSQL with scan_id. |
| | IAM, S3, and Lambda enumeration data stored in MongoDB. |
| | Scan available for viewing results and attack path analysis. |

### **Use Case Cross referenced**

- **UC-SCAN-02:** User can view created scan in list.
- **UC-SCAN-03:** User can view detailed scan results.
- **UC-SCAN-04:** Includes AWS enumeration subprocess.
- **UC-AI-01:** Scan results used for attack path generation.

---

## **<UC-SCAN-02>**

| Use case Id: | UC-SCAN-02 |
|--------------|------------|
| **Actors:** | Security Analyst: Views scan history |
| **Feature:** | List Scans |
| **Pre-condition:** | User must be logged in. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst navigates to scans page. | System queries PostgreSQL for user's scans ordered by created_at DESC. |
| **2.** | System retrieves scan list. | Displays list with scan ID, environment name, status, and creation date. |

**Alternate Scenarios:**
- **2a: If no scans exist, system displays message: "No scans found. Create your first scan."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | User views all their security scans. |

### **Use Case Cross referenced**

- **UC-SCAN-01:** Create Scan adds to this list.
- **UC-SCAN-03:** User can click scan to view results.

---

## **<UC-SCAN-03>**

| Use case Id: | UC-SCAN-03 |
|--------------|------------|
| **Actors:** | Security Analyst: Views detailed scan results |
| **Feature:** | View Scan Results |
| **Pre-condition:** | User must be logged in. Scan must exist and belong to user. Scan must be completed. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst selects scan from list. | System validates scan ownership and retrieves scan_id. |
| **2.** | System queries MongoDB using ThreadPoolExecutor. | Fetches 6 collections concurrently: iam_users, iam_roles, iam_groups, s3_buckets, lambda_functions, lambda_layers. |
| **3.** | System maps MongoDB documents to dataclass objects. | Converts raw documents using ScanResultMapper. |
| **4.** | System displays results. | Shows IAM users/roles/groups with policies, S3 buckets with permissions, Lambda functions with configurations. |

**Alternate Scenarios:**
- **1a: If scan not found or unauthorized, system displays error: "Scan not found or unauthorized access."**
- **2a: If MongoDB connection fails, system displays error: "Failed to retrieve scan results."**
- **3a: If no results found for scan_id, system displays message: "No scan data available."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | User views comprehensive AWS resource enumeration data. |
| | Data formatted and ready for manual review or AI analysis. |

### **Use Case Cross referenced**

- **UC-SCAN-04:** Results generated by enumeration process.
- **UC-AI-01:** Results can be analyzed for attack paths.

---

## **<UC-SCAN-04>**

| Use case Id: | UC-SCAN-04 |
|--------------|------------|
| **Actors:** | AWS API: Provides resource enumeration data |
| **Feature:** | Run AWS Enumeration |
| **Pre-condition:** | AWS credentials must be valid. AWS API must be accessible. Scan request initiated from UC-SCAN-01. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | System initiates IAM enumeration module. | Calls AWS IAM API using boto3 to list users, roles, groups. |
| **2.** | IAM module fetches policies and permissions. | Retrieves managed policies, inline policies, access keys, assume role policies. |
| **3.** | System initiates S3 enumeration module. | Calls AWS S3 API to list buckets, policies, ACLs, encryption config. |
| **4.** | System initiates Lambda enumeration module. | Calls AWS Lambda API to list functions, layers, environment variables, VPC configs. |
| **5.** | All modules complete enumeration. | System stores results in MongoDB with scan_id reference. |

**Alternate Scenarios:**
- **1a: If IAM permissions insufficient, system logs specific IAM errors and continues with available data.**
- **2a: If S3 access denied, system logs error and continues.**
- **3a: If Lambda enumeration fails, system logs error and continues.**
- **5a: If MongoDB storage fails, system displays error: "Failed to store scan results."**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Complete AWS resource inventory stored in MongoDB. |
| | Data includes IAM policies, S3 configurations, Lambda settings. |

### **Use Case Cross referenced**

- **UC-SCAN-01:** Enumeration triggered by scan creation.
- **UC-SCAN-03:** Results available for viewing.

---

## **<UC-AI-01>**

| Use case Id: | UC-AI-01 |
|--------------|------------|
| **Actors:** | Security Analyst: Requests attack path analysis |
| **Feature:** | Generate Attack Paths |
| **Pre-condition:** | User must be logged in. Scan must be completed with results. Gemini API key must be configured. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst selects "Generate Attack Paths" for a scan. | System retrieves scan results from UC-SCAN-03. |
| **2.** | System preprocesses enumeration data (UC-AI-02). | Reduces data size by 70-80%, removes AWS metadata noise. |
| **3.** | System performs risk analysis (UC-AI-03). | Calculates risk scores and identifies high-risk patterns. |
| **4.** | System performs multi-stage LLM analysis (UC-AI-04). | Executes 3-stage pipeline with Gemini AI. |
| **5.** | System displays results. | Shows severity level, attack paths, exploitation commands, and recommendations. |

**Alternate Scenarios:**
- **1a: If scan not found or unauthorized, system displays error: "Scan not found."**
- **2a: If preprocessing fails, system logs error and attempts analysis with raw data.**
- **4a: If LLM returns low severity, system skips deep analysis and shows triage results only.**
- **4b: If Gemini API fails or content blocked by safety filters, system displays error with fallback recommendations.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Attack paths generated and displayed. |
| | Security analyst has actionable exploitation steps. |
| | AWS CLI commands ready for testing. |

### **Use Case Cross referenced**

- **UC-SCAN-03:** Uses scan results as input.
- **UC-AI-02:** Includes data preprocessing.
- **UC-AI-03:** Includes risk analysis.
- **UC-AI-04:** Includes multi-stage LLM analysis.

---

## **<UC-AI-02>**

| Use case Id: | UC-AI-02 |
|--------------|------------|
| **Actors:** | System: Automated data preprocessing |
| **Feature:** | Preprocess Enumeration Data |
| **Pre-condition:** | Raw scan results must be available. DataPreprocessor module must be initialized. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | System receives raw enumeration data (dataclass objects). | Converts dataclass objects to dictionaries using asdict(). |
| **2.** | System applies cleaning algorithms. | Recursively removes AWS metadata (ResponseMetadata, HTTPHeaders, RequestId, etc.). |
| **3.** | System extracts security-relevant fields. | Filters IAM policies, S3 permissions, Lambda configurations. |
| **4.** | System returns processed data. | Reduced JSON payload (70-80% smaller) with only security-critical information. |

**Alternate Scenarios:**
- **2a: If data structure unexpected, system logs warning and continues with available fields.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Clean, compact data ready for LLM analysis. |
| | Token count reduced significantly for cost optimization. |

### **Use Case Cross referenced**

- **UC-AI-01:** Preprocessing is first step in attack path generation.
- **UC-AI-03:** Preprocessed data used for risk analysis.

---

## **<UC-AI-03>**

| Use case Id: | UC-AI-03 |
|--------------|------------|
| **Actors:** | System: Automated risk scoring |
| **Feature:** | Analyze Security Risks |
| **Pre-condition:** | Preprocessed data must be available. RiskAnalyzer module must be initialized. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | System receives preprocessed data. | RiskAnalyzer initializes with HIGH_RISK_POLICIES and DANGEROUS_ACTIONS configs. |
| **2.** | System scores IAM configurations. | Checks for wildcard permissions (*:*), AdministratorAccess, overly permissive policies. |
| **3.** | System scores S3 configurations. | Checks for public buckets, missing encryption, permissive ACLs. |
| **4.** | System scores Lambda configurations. | Checks for environment variables with secrets, missing VPC, overly permissive roles. |
| **5.** | System calculates overall severity. | Aggregates scores: 0-100 scale (critical/high/medium/low). |
| **6.** | System returns risk summary. | Generates findings list with severity, resource, detail, and impact. |

**Alternate Scenarios:**
- **5a: If no high-risk findings, severity is "low" and deep analysis may be skipped.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Risk summary generated with severity level. |
| | Findings prioritized by exploitability. |

### **Use Case Cross referenced**

- **UC-AI-01:** Risk analysis feeds into attack path generation.
- **UC-AI-04:** Risk summary used in Stage 1 triage.

---

## **<UC-AI-04>**

| Use case Id: | UC-AI-04 |
|--------------|------------|
| **Actors:** | Gemini AI: Performs multi-stage security analysis |
| **Feature:** | Multi-Stage LLM Analysis |
| **Pre-condition:** | Risk summary must be available. Gemini API key must be valid. PromptConstructor and GeminiClient must be initialized. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | System performs Stage 1: Triage (UC-AI-05). | Quick risk assessment (2-3 seconds). |
| **2.** | System checks triage severity. | If severity is critical/high OR requires_deep_analysis=true, proceed to Stage 2. |
| **3.** | System performs Stage 2: Deep Analysis (UC-AI-06). | Detailed attack path identification (10-15 seconds). |
| **4.** | System performs Stage 3: Command Generation (UC-AI-07). | AWS CLI exploitation commands (5 seconds). |
| **5.** | System returns complete analysis. | JSON response with triage, analysis, commands, and risk summary. |

**Alternate Scenarios:**
- **2a: If severity is low/medium, system skips Stage 2 and Stage 3, returns triage only.**
- **3a: If deep analysis returns error, system logs error and returns partial results.**
- **4a: If command generation blocked by safety filters, system returns analysis without commands.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Complete security analysis with actionable steps. |
| | Attack paths documented with prerequisites and impact. |

### **Use Case Cross referenced**

- **UC-AI-01:** Multi-stage analysis is core of attack path generation.
- **UC-AI-05:** Stage 1 Triage subprocess.
- **UC-AI-06:** Stage 2 Deep Analysis subprocess.
- **UC-AI-07:** Stage 3 Command Generation subprocess.

---

## **<UC-AI-05>**

| Use case Id: | UC-AI-05 |
|--------------|------------|
| **Actors:** | Gemini AI: Performs quick triage |
| **Feature:** | Stage 1: Triage |
| **Pre-condition:** | Risk summary must be available. stage1_triage.txt prompt template must exist. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | System loads stage1_triage.txt template. | PromptConstructor reads template from genai/templates/. |
| **2.** | System constructs triage prompt. | Injects risk_summary JSON into template placeholders. |
| **3.** | System calls Gemini API. | Sends prompt with temperature=0.3, max_tokens=1024. |
| **4.** | Gemini AI analyzes risk patterns. | Identifies top 3 entry points ranked by exploitability. |
| **5.** | System extracts JSON response. | Parses severity, entry_points, quick_wins, requires_deep_analysis flag. |

**Alternate Scenarios:**
- **3a: If API call fails, system returns error object with severity="unknown".**
- **4a: If content blocked by safety filters, system returns graceful fallback.**
- **5a: If JSON parsing fails, system attempts regex extraction or returns error.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Quick triage completed with severity assessment. |
| | Decision made on whether deep analysis needed. |

### **Use Case Cross referenced**

- **UC-AI-04:** Triage is Stage 1 of multi-stage analysis.
- **UC-AI-06:** Triage results feed into deep analysis.

---

## **<UC-AI-06>**

| Use case Id: | UC-AI-06 |
|--------------|------------|
| **Actors:** | Gemini AI: Performs deep security analysis |
| **Feature:** | Stage 2: Deep Analysis |
| **Pre-condition:** | Triage indicates high risk. Preprocessed data and triage results available. stage2_analysis.txt template must exist. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | System loads stage2_analysis.txt template. | PromptConstructor reads detailed analysis template. |
| **2.** | System constructs analysis prompt. | Injects scan_id, triage_result, and processed_data into template. |
| **3.** | System calls Gemini API. | Sends prompt with temperature=0.4, max_tokens=4096. |
| **4.** | Gemini AI performs deep analysis. | Identifies attack paths (max 5), cross-service risks, data exposure, privilege escalation chains. |
| **5.** | System extracts JSON response. | Parses attack_paths array with steps, resources, prerequisites, impact, and recommendations. |

**Alternate Scenarios:**
- **3a: If API call fails, system returns error with empty attack_paths array.**
- **4a: If content blocked, system returns fallback with basic recommendations.**
- **5a: If no attack paths found, system returns empty array with explanation.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Detailed attack paths documented with step-by-step exploitation. |
| | Cross-service vulnerabilities identified. |

### **Use Case Cross referenced**

- **UC-AI-04:** Deep analysis is Stage 2 of multi-stage analysis.
- **UC-AI-07:** Attack paths used for command generation.

---

## **<UC-AI-07>**

| Use case Id: | UC-AI-07 |
|--------------|------------|
| **Actors:** | Gemini AI: Generates exploitation commands |
| **Feature:** | Stage 3: Generate Commands |
| **Pre-condition:** | Attack paths must be available from Stage 2. stage3_commands.txt template must exist. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | System loads stage3_commands.txt template. | PromptConstructor reads command generation template. |
| **2.** | System constructs command prompt. | Injects attack_paths JSON into template. |
| **3.** | System calls Gemini API. | Sends prompt with temperature=0.2, max_tokens=2048. |
| **4.** | Gemini AI generates AWS CLI commands. | Creates exploitation_commands and validation_commands arrays. |
| **5.** | System extracts JSON response. | Parses commands with path_id, step, description, command, expected_output. |

**Alternate Scenarios:**
- **3a: If API call fails, system returns error with empty commands array.**
- **4a: If content blocked by safety filters, system returns error message.**
- **5a: If JSON parsing fails, system returns structured error.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | Copy-paste ready AWS CLI v2 commands available. |
| | Each command includes expected output for validation. |
| | Commands organized by attack path for clarity. |

### **Use Case Cross referenced**

- **UC-AI-04:** Command generation is Stage 3 of multi-stage analysis.
- **UC-AI-01:** Commands returned in final attack path response.

---

## **<UC-AUTH-03>**

| Use case Id: | UC-AUTH-03 |
|--------------|------------|
| **Actors:** | Security Analyst: Ends session |
| **Feature:** | Logout |
| **Pre-condition:** | User must be logged in with active JWT token. |

### **Scenarios**

| Step# | Action | Software Reaction |
|-------|--------|-------------------|
| **1.** | Security Analyst clicks "Logout" button. | System clears JWT token from client storage. |
| **2.** | System invalidates session. | Redirects user to login page. |

**Alternate Scenarios:**
- **1a: If already logged out, system redirects to login page.**

### **Post Conditions**

| Step# | Description |
|-------|-------------|
| | User session terminated. |
| | JWT token removed from client. |
| | User must login again to access protected resources. |

### **Use Case Cross referenced**

- **UC-AUTH-02:** Login creates session that logout terminates.

---

