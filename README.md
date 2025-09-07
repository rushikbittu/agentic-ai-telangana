#  Agentic AI Telangana

A **Real-Time Governance System (RTGS)** for policymakers in Telangana, powered by **agentic AI**.  
This system ingests **public datasets from the Telangana Open Data Portal**, dynamically plans and executes data pipelines, generates insights, and supports **natural language Q&A**.

---

##  Features

- **Dynamic Orchestration**  
   LLM-driven Orchestrator decides which modules to call (`ingestion`, `cleaning`, `transformation`, `insights`) depending on the dataset and user goals.

- **Feedback Loops**  
  If cleaning fails (e.g., too many missing values), the system:
  - Re-ingests or retries automatically  
  - Suggests alternate datasets  
  - Logs all corrective actions

- **Goal-Driven Behavior**  
  Instead of just running a pipeline, the system executes **user goals**:  
  > *Example:*  
  > User asks: *“Give me rainfall trends in drought-prone districts only”*  
  > → Agent decides: filter dataset → transform → generate chart → return insights.

- **Data Quality Flags**  
  - `_qc_missing`: missing values  
  - `_qc_outlier`: detected outliers  
  - `_qc_imputed`: imputed rows  

- **Insights & Visuals**  
  - Auto-generated **summary reports** (`summary.md`)  
  - **Charts** (e.g., rainfall/time trends in `plot.png`)  
  - **Provenance tracking** inside `run_artifacts/`

- **Interactive Q&A**  
  After the pipeline runs, you can ask natural language questions:  
