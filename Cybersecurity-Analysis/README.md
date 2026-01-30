Cybersecurity Data Analytics Project
Welcome to my Cybersecurity Data Analytics Project, where I leverage data engineering, exploratory analysis, natural language processing (NLP), and root cause analysis (RCA) to transform raw cybersecurity data into actionable insights. This project is designed as an end-to-end solution covering data simulation, analytics, and visualizations to help decision-makers identify areas of improvement, optimize operations, and track key performance indicators (KPIs).

Project Overview
The project is implemented specifically for the cybersecurity department of a bank to improve operational efficiency and provide insights into key metrics such as:

Volume trends: Ticket distribution over time.
Busiest days: Pinpoint peak operational times.
Reopen analysis: Track recurring incidents and inefficiencies.
KPI breaches: Monitor failures against SLA thresholds.
Root cause analysis: Identify underlying factors for delays, failures, and breaches.
Bigram text analysis: Identify recurring text patterns in incident descriptions for trend identification.
The solutions rely on data-driven decision-making using structured workflows and modern tools to:

Automate reporting.
Enable proactive resolutions.
Improve SLA compliance.
Key Features
### 1. Data Generation
Synthetic Data Simulation:
Created a customized cybersecurity incident dataset covering a full year.
Each record includes fields such as:
Created, Start Date, Closed: Timestamps for ticket lifecycle.
Priority, Risk, Urgency, Impact: Operational metrics tied to SLA compliance.
Short Description: Incident descriptions used for NLP.
Assignment Group, Requested By, Change Environment: Key identifiers for RCA.
Logical time relationships are maintained (e.g., Start Date > Created > Closed).
Used Python (datetime, random, Polars`) for efficient data generation.
### 2. Exploratory Data Analysis (EIDA)
Calculated Metrics:
Time to Response Hours: Time between ticket creation (Created) and work start (Start Date).
Processing Time Hours: Time between work start (Start Date) and ticket closure (Closed).
Total Time Hours: Complete lifecycle duration from creation to closure.
KPI Breach Tracking:
Dynamically mapped processing time thresholds (Critical, High, Medium, Low) to create KPI_breach flags.
Provided averages and summary statistics for performance tracking.
Inconsistency Checks:
Identified tickets where timestamps violated logical relationships (e.g., Created > Start Date).
### 3. NLP Analysis
Text Preprocessing:
Tokenized Short Description text using SpaCy.
Removed stopwords, punctuation, and numeric tokens using custom filters.
Bigram Analysis:
Used CountVectorizer (Scikit-learn) to extract two-word phrases (bigrams) from descriptions.
Sorted bigrams by frequency to identify recurring text themes, such as "failed encryption", "login failure", etc.
Output Insights:
Provided a ranked list of the top bigram patterns for incident trend analysis.
### 4. Root Cause Analysis (RCA)
Multi-Dimensional Analysis:
Analyzed ticket failures (KPI_breach = 1) across categories such as:
Priority (Critical, High, Medium, Low).
Assignment Group (team-specific analysis).
Reopen Count (repeat incidents).
Risk Level (High, Medium, Low).
Day of the Week (Created-based trend analysis).
Calculated breach rates, percentages, and average processing times for actionable insights.
Reopen Analysis:
Highlighted assignment groups contributing to recurring issues.
Risk-Level Analysis:
Identified high-risk tickets causing SLA breaches and highlighted operational gaps.
Day-Based Trends:
Provided insights into busiest days and recurring performance issues.
Technologies Used
Programming Languages & Libraries
Python:
Data Engineering: datetime, random.
Analytics & Processing: Polars, os.
NLP Analysis: SpaCy, Scikit-learn.
Tools & Solutions
Power BI:
Scalable dashboards for visualizing SLA inefficiencies, KPI breaches, priority metrics, and day-based trends.
Polars:
Optimal for fast, large-scale data manipulation and metrics calculations.
GitHub:
Source control and versioning for project sharing.
Project Workflow
The project is organized into four structured segments, ensuring a professional, scalable approach:

1. Data Generation
Randomized incident ticket dataset for realistic simulations.
Logical time relationships maintained (Start Date > Created > Closed).
Fields included for incident tracking and RCA.
2. EIDA Analysis
Predefined metrics (Time to Response, Processing Time, Total Time).
SLA compliance tracked via calculated KPI_breach.
Null, duplicate, and inconsistency checks for data integrity.
3. NLP Analysis
Cleaned text-based incident descriptions (Short Description) using SpaCy.
Extracted bigrams to identify recurring issue patterns.
4. Root Cause Analysis
RCA performed across multiple dimensions:
KPI breaches by priority, assignment groups, and risk levels.
Reopen trend analysis.
Time-based trends by day of the week.
Key Insights From Project
1. SLA Compliance Insights

Processed breaches by Priority:
Critical incidents most often fail SLA thresholds. 2. Operational Bottlenecks
Assignment groups with high delays (e.g., breaches or reopens). 3. Incident Patterns
Extracted textual patterns in descriptions (e.g., "failed encryption") for proactive analysis.
How To Use This Project
Setup Instructions
Clone the repository:

copy
git clone https://github.com/<your-username>/Cybersecurity-EIDA-Project.git
cd Cybersecurity-EIDA-Project
Install dependencies:

copy
pip install polars spacy scikit-learn
python -m spacy download en_core_web_sm
Run Files
Generate data using Data_Generation.py:
Creates a simulated dataset (synthetic_cybersecurity_bank_data.csv).
EIDA analysis using EIDA_Analysis.py:
Perform exploratory analysis and calculate key metrics.
NLP analytics using NLP_Analysis.py.
RCA insights with Root_Cause_Analysis.py.
Future Enhancements
Incorporate ML models to predict breaches and inefficiencies.
Use unsupervised learning (topic modeling) for textual data (Short Description).
Integrate advanced dashboards (e.g., time series insights).
Resources
Official ITIL Framework Documentation:
For SLA and incident management recommendations.
Polars Documentation:
Polars Official Docs.
SpaCy Documentation:
SpaCy NLP Library.
Scikit-Learn Documentation:
Scikit-learn.
Contact
If you have feedback or questions, feel free to reach out:

Email: yourname@email.com
LinkedIn: linkedin-profile
GitHub: github-profile# Cybersecurity Analysis Project

## Objective
Provide comprehensive analysis of cybersecurity incidents, focusing on detection, response, and prevention strategies.

## Key Features
- Incident response time tracking
- Incident processing time tracking & analysis
- Root cause investigation
- Security KPI monitoring

## Technologies
- Python
- Power BI Dashboards
