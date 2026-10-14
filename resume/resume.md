---
name: "Kenny Chou, Ph.D."
email: "kennethfchou@gmail.com"
phone: "916-258-2468"
linkedin: "@kenny-chou"
github: "@kfchou"
web: "kfchou.github.io"
---

<!--
TAILORED FOR: Machine Learning Engineer — Layer Health (LLM chart review / clinical registry abstraction)
JD: https://job-boards.greenhouse.io/layerhealth/jobs/4915887008
Angle: production LLM systems on clinical data + the eval / observability / reliability layer
(JD: "detect drift/performance degradation", "observability tooling", "monitoring, logging, and error handling").
Backend/cloud depth is the JD's stated gap — carried by Philips AWS, Lab378, and Project Alligator bullets.
Title honesty: Philips title stays "Data Scientist" + descriptor (see wiki level-vs-salary-vs-domain-2026-10).
-->

## Summary

ML engineer with a Ph.D. in biomedical engineering and 5+ years shipping production ML on clinical and wearable-health data, including EHR data and FDA-constrained algorithms. Builds LLM systems end to end, including evaluation, LLM-as-judge grading, and grounding agent output in cited evidence. Creator of wiki-skills (185+★), an open-source agent context and memory toolkit now deployed inside Philips.

## Technical Skills

- **LLM systems & evaluation**: multi-agent systems, structured outputs (Pydantic), document ingestion and extraction, context & memory engineering, LLM-as-judge, A/B evals, regression testing, agent observability; OpenAI / Anthropic APIs, PydanticAI.
- **Backend & cloud**: Python, FastAPI, Django, event-driven ingestion (webhooks, task queues), multi-tenant platforms; AWS (CDK, CloudFormation, GovCloud, S3, Redshift), GCP (Cloud Run, Cloud Functions, Firestore); Docker, CI/CD, test-driven development.
- **Clinical & health data**: EHR datasets, clinical-study data, physiological time series (PPG, ECG, capnography), FDA-constrained algorithm development, data quality and reproducibility.
- **ML & data**: statistical modeling, feature engineering, regression/classification, LSTMs, forecasting, signal processing; SQL, Databricks, NumPy, Pandas, scikit-learn.

## Relevant Projects

### Project Alligator — LLM Extraction over Medical Records  `2025`
*Founding engineer · 4-person team · Python, FastAPI, OpenAI, Firebase, GCP*

- Owned the full technical build of a multi-agent LLM system that ingests medical bills, EOBs, and medical records, removes PII, detects billing errors (upcoding, unbundling, CPT miscoding), and generates appeal letters and phone scripts.
- Enforced LLM responses as structured-outputs (Pydantic), making them typed and machine-validatable.
- Built the FastAPI backend (Firebase Auth / Firestore / Storage) with a PDF and image ingestion pipeline; deployed to Google Cloud Run through Dockerized CI/CD with a pytest suite.

### AI Research & Portfolio Agents — Public-Equity Due Diligence  `2026–present`
*Co-designer & primary analyst · 4-person team · Python, Claude Code, React/TypeScript*

- Co-designed a multi-step agentic reasoning system that gathers market and macro data, synthesizes cited research reports, and fact-checks every AI-generated analysis before use; built on the wiki-skills architecture.
- Built data pipelines for SEC filings, earnings transcripts, macro series (FRED, CFTC positioning), and market indicators (prices, option chain, short interest), feeding 240+ processed sources.
- Authored the agent skills for source ingestion, querying, updating, and fact-checking; produced 90+ company research reports.
- Validated each skill change with A/B tests and LLM-as-judge grading.
- Built a private portfolio agent that scores holdings against a recommendation rubric, driving go/no-go and sizing decisions for 30+ equities.

### wiki-skills — Context & Memory Engineering for LLM Agents  `2026–present`
*Open source · 187 stars · 29 forks · github.com/kfchou/wiki-skills*

- Authored a toolkit that turns unstructured sources into a schema-enforced, cited knowledge base through multi-step agentic workflows, keeping agents grounded across long-running tasks without vector search.
- Deployed in three settings: open source, the synthesis layer of the due-diligence system above, and internal tooling at Philips.

## Experience

### Koninklijke Philips N.V., Cambridge, MA `01/2024–present`
*Data Scientist (ML Engineering & Applied AI) — wearable devices*

* Built and deployed an internal LLM context and documentation tool (based on wiki-skills) for 2 teams (~15 data scientists and engineers) working on a 5-year-old codebase deployed to multiple AWS systems; extended it to guide 3 external partners building plugins, with ADRs enforced in CI on feature branches.
* Supplied coding agents with structured context for a sparsely documented codebase, reducing wrong edits and search overhead and making the team self-sufficient on code that previously required senior support.
* Own customer-facing AWS infrastructure as code (CDK, CloudFormation) for live production services used by 5,000+ users, including a repeatable, documented process for per-tenant production stacks isolated from staging.
* Partnered with the system architect to deploy cross-partition networking between commercial AWS and AWS GovCloud for CMMC 2.0 compliance: sensitive compute runs in GovCloud, reading from and writing back to commercial S3.
* Hardened a research-grade ML pipeline for production with testing, CI, and security reviews.
* Developed and deployed ML pipelines for respiratory-illness prediction from commercial wearables.
* Lead code review and engineering standards for ML and software across research and development teams.

### Lab378, Remote `07/2025–05/2026` *(contract, part-time)*
*Member of Technical Staff — voice-AI sales agents for real estate*

* Designed and shipped a production multi-tenant billing/ETL platform as sole author: FastAPI on Google Cloud Functions (Gen2) ingesting CRM (FollowUpBoss) and e-signature (BoldSign) webhooks into Firestore, with HMAC signature verification, task queues, and a Django invoicing dashboard.
* Advised on voice-AI and applied-AI architecture for the company's autonomous sales-agent product.

### Current Health, Boston, MA `09/2021–03/2023`
*Applied Data Scientist — Biomedical Engineering*

- Improved wearable biomarker-estimation accuracy by over 35% within FDA constraints while cutting associated compute cost by over 50%.
- Designed and built an ELT pipeline (Python, SQL) with the software team for repeatable, semi-automated reporting over large EHR datasets, reducing manual effort by over 80%.
- Implemented ML models (regression, classification, LSTMs, forecasting) on large-scale clinical and sensor time series to prototype smart alarms for early event detection.
- Led the effort to resolve data inconsistencies across teams, establishing processes for data quality and reproducibility.
- Delivered clinical and operational insights for quarterly business reviews that helped extend and expand contracts worth $3MM.

### Global Health Labs, Bellevue, WA `02/2021–09/2021, 04/2023–01/2024`
*Clinical Data Scientist*

- Built Python models extracting digital biomarkers (respiratory rate, HR, HRV) from noisy, real-world physiological data (PPG, capnography) using DSP, statistical learning, and feature engineering.
- Built the pipeline to clean, time-align, filter, and analyze raw clinical-study data.
- Shaped study design and endpoints with an international team of engineers, clinicians, and study coordinators.

### Sen Lab, Boston University `05/2016–05/2021`
*Graduate Research Fellow*

- Designed a novel speech-segregation algorithm benchmarked against ML and deep-learning models (published in JARO; US Patent No. 10,536,775).
- Researched optimizing spiking neural networks through transfer learning from DNNs.
- Supervised 3 junior research fellows; results contributed to NIH R34 and NSF awards totaling $1.7M.

## Education

| | |
|---|---|
| **Boston University** | Thesis: Biological Neural Networks for Background Speech Suppression |
| Ph.D., Biomedical Engineering, 2020 | Distinguished Biomedical Engineering Fellow (2013) |
| M.S., Biomedical Engineering, 2017 | Google Scholar: <https://bit.ly/3gazuB2> |
| **University of Washington** | |
| B.S., Biomedical Engineering, 2013 | Washington Research Foundation Fellow (2011, 2012) |
| B.S., Electrical Engineering, 2013 | |
| Minor in Mathematics | |
