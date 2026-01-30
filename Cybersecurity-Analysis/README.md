# Cybersecurity Data Analytics Project

Welcome to my **Cybersecurity Data Analytics Project**, where I leverage **data engineering**, **exploratory analysis**, **natural language processing (NLP)**, and **root cause analysis (RCA)** to transform raw cybersecurity data into actionable insights. This project is designed as an **end-to-end solution** covering **data simulation**, **analytics**, and **visualizations** to help decision-makers identify areas of improvement, optimize operations, and track key performance indicators (KPIs).

---

## Project Overview

This project tackles challenges faced by a **cybersecurity department in a bank**, focusing on key metrics such as:
- **Volume trends**: Ticket distribution over time.
- **Busiest days**: Pinpoint peak operational times.
- **Reopen analysis**: Track recurring incidents and inefficiencies.
- **KPI breaches**: Monitor failures against SLA thresholds.
- **Root cause analysis**: Identify underlying factors for delays, failures, and breaches.
- **Bigram text analysis**: Identify recurring text patterns in incident descriptions for trend identification.

By employing **data-driven decision-making**, this project provides structured workflows and insights that:
1. **Automate reporting**.
2. **Enable proactive resolutions**.
3. **Improve SLA compliance**.

---

## Key Features

### 1. Data Generation
- **Synthetic Data Simulation**:
  - Created a customized **cybersecurity incident dataset** covering a full year.
  - Fields include `Created`, `Start Date`, `Closed` timestamps, `Priority`, `Risk`, `Urgency`, `Impact`, `Short Description`, and more.
  - Logical time relationships are maintained (e.g., `Start Date > Created > Closed`).
  - Used Python (`datetime`, `random`, Polars`) for efficient data generation.

### 2. Exploratory Data Analysis (EIDA)
- **Calculated Metrics**:
  - **Time to Response Hours**: Time between ticket creation (`Created`) and work start (`Start Date`).
  - **Processing Time Hours**: Time between work start (`Start Date`) and ticket closure (`Closed`).
  - **Total Time Hours**: Complete lifecycle duration from creation to closure.
- **KPI Breach Tracking**:
  - Dynamically mapped processing time thresholds (`Critical`, `High`, `Medium`, `Low`) to create `KPI_breach` flags.
  - Provided averages and summary statistics for performance tracking.
- **Inconsistency Checks**:
  - Identified tickets where timestamps violated logical relationships (e.g., `Created > Start Date`).

### 3. NLP Analysis
- **Text Preprocessing**:
  - Tokenized `Short Description` text using **SpaCy**.
  - Removed stopwords, punctuation, and numeric tokens using custom filters.
- **Bigram Analysis**:
  - Used `CountVectorizer` (Scikit-learn) to extract **two-word phrases (bigrams)** from descriptions.
  - Sorted bigrams by frequency to identify recurring issue patterns.

### 4. Root Cause Analysis
- **Multi-Dimensional Analysis**:
  - Analyzed ticket failures (`KPI_breach = 1`) across categories such as:
    - **Priority**: Critical, High, Medium, Low.
    - **Assignment Group**: Reviewed group-specific performance on breaches.
    - **Reopen Count**: Highlighted recurring and unresolved issues.
    - **Risk Level**: High, Medium, and Low risks leading to failures.
    - **Day of the Week**: Trends based on ticket creation time (`Created`).
  - Provided breach rates, percentages, and average processing times for each dimension.

---

## Technologies Used

### Programming Languages & Libraries:
- **Python**:
  - Data Engineering: `datetime`, `random`.
  - Analytics & Processing: `Polars`, `os`.
  - NLP Analysis: `SpaCy`, `Scikit-learn`.

### Tools & Solutions:
- **Power BI**:
  - Scalable dashboards for visualizing SLA inefficiencies, KPI breaches, priority metrics, and day-based trends.
- **Polars**:
  - Optimal for fast, large-scale data manipulation and metrics calculations.

---

## Project Workflow

This project follows a **well-structured workflow**:
1. **Data Generation**:
   - Randomized incident ticket dataset for realistic simulations.
   - Logical time relationships maintained (`Start Date > Created > Closed`).
2. **Exploratory Data Analysis (EIDA)**:
   - Predefined metrics (`Time to Response`, `Processing Time`, `Total Time`).
   - SLA compliance and KPI breaches identified.
   - Null, duplicate, and inconsistency checks performed.
3. **NLP Analysis**:
   - Cleaned text-based incident descriptions (`Short Description`) using SpaCy.
   - Extracted bigrams to identify recurring issue patterns.
4. **Root Cause Analysis**:
   - RCA performed across multiple dimensions, including KPIs and reopen trends.

---

## Key Insights From Project

### SLA Compliance Insights:
- Processed breaches by `Priority`:
  - Example output showing "Critical" incidents most often failing SLA thresholds.

### Operational Bottlenecks:
- Assignment groups contributing most to KPI breaches or ticket delays.

### Incident Patterns:
- Extracted textual patterns such as `"failed encryption"` or `"login failure"` for proactive analysis.

---

## How To Use This Project

### Setup Instructions:
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/Cybersecurity-EIDA-Project.git
   cd Cybersecurity-EIDA-Project
