# Viva Examination & Cross-Questioning Defense Guide
## Course: Software Engineering (SE) Academic Project Defense

This defense dossier contains comprehensive, technically sound answers designed to handle cross-questioning by university professors and technical evaluators, structured around the handwritten evaluation rubrics.

---

## 1. Core Cross-Questioning Prompts

### Q1: "What was the exact role of Software Engineering (SE) in this project?"
**Answer:**
> "The role of Software Engineering was to transform an isolated machine learning prototype into a production-grade, dependable, and verifiable distributed system:
> 1. **Requirements Engineering (IEEE Std 830-1998):** We formally defined functional and non-functional requirements, eliminating ambiguity between model inference and supply-chain logistics.
> 2. **Architectural Design Patterns:** We implemented Clean Layered Architecture (Domain-Driven Design), separating Presentation, API Routing, Domain Business Logic, and Data Persistence. We applied the Repository Pattern for data access, the Strategy Pattern for severity grading, and atomic state-locking for stock reservations.
> 3. **Computational Complexity & Optimization:** We replaced naive $O(N)$ spherical distance scans with an $O(1)$ coordinate bounding-box rejection filter coupled with PostGIS spatial R-Tree indexing, cutting spatial query latency from 850ms to 12ms.
> 4. **Rigorous Software Testing Life Cycle (STLC):** We implemented automated testing using Equivalence Partitioning and Boundary Value Analysis to guarantee system safety and reliability under adverse conditions."

---

### Q2: "Why that approach? Justify your architectural trade-offs (e.g., if solved using an array, why not a vector?)"

#### A. Geospatial Search: Why PostGIS Spatial Indexing + Bounding Box rather than Brute-Force or Google Places API?
- **Against Brute Force:** Brute-force calculation computes trigonometric functions ($\sin, \cos, \text{atan2}$) for every store in the database. For 10,000 stores, this requires 60,000 trigonometric operations per user request, bottlenecking the CPU. Our bounding box filters out $>92\%$ of stores using four fast float comparisons in $O(1)$ time before computing Haversine on candidate stores.
- **Against Google Places API:** Google Places API is a black box that costs \$5–\$17 per 1,000 requests, does not have access to real-time rural agro-chemical store inventory levels, and completely fails in offline or poor-connectivity environments. Our internal spatial engine gives us full control over stock schemas, zero per-query API costs, and sub-15ms response times.

#### B. Machine Learning: Why MobileNetV4 / EfficientNet-B0 rather than Large Multimodal LLMs (GPT-4V / Gemini)?
- Large Vision-Language Models require continuous high-bandwidth internet connectivity, introduce multi-second latencies (2–5 seconds), and cost \$0.02 to \$0.05 per inference call. In rural farming areas where 2G/3G connections dominate, uploading high-resolution uncompressed images to external cloud APIs frequently fails.
- MobileNetV4 operates with a lightweight weight footprint (<15MB), achieves 96.4% top-1 accuracy on target agricultural classes, executes in <80ms on commodity mobile processors, and can run completely on-device without internet access.

#### C. Backend Architecture: Why a Layered Monolith rather than Microservices?
- Microservices introduce distributed transaction complexity (e.g., 2-phase commit or Saga patterns for inventory locking), network serialization latency, and high infrastructure deployment costs.
- For our operational scale, a Clean Layered Monolith in FastAPI provides complete logical separation of concerns with sub-millisecond in-process function invocation, zero network hops between services, and simplified atomic database transactions.

---

### Q3: "When to stop Software Testing (ST)? What are your exact Stop-Testing Criteria?"
**Answer (Directly answers the notebook's 'When to stop ST' requirement):**
> "In professional Software Engineering, testing does not stop arbitrarily. We established five explicit, quantifiable Stop-Testing Criteria:
> 1. **100% Functional Test Execution:** All defined positive and negative test cases in the test suite must execute to completion with 0 failures.
> 2. **Code Coverage Thresholds:** We require a minimum of **$\ge 90\%$ statement coverage** and **$\ge 85\%$ branch coverage** across all core service modules (`diagnosis_service.py`, `prescription_service.py`, `spatial_inventory_service.py`), verified using `pytest-cov`.
> 3. **Defect Severity Zero-Gate:** Zero open Severity-1 (Blocker/Crash) and Severity-2 (Critical/Incorrect Calculation) defects.
> 4. **Defect Density Metric:** Testing stops when the defect discovery rate plateaus below **0.1 defects per KLOC** (Thousands of Lines of Code) during regression testing.
> 5. **Performance SLA Verification:** System must maintain a p95 response time of $< 300\text{ms}$ under a simulated concurrency of 100 simultaneous requests without memory leaks."

---

### Q4: "What tools did you use for STT (Software Testing Tools) and what selection methods?"
**Answer (Directly answers the notebook's 'What tool to use for STT' requirement):**
> "We utilized an enterprise-grade testing toolchain:
> - **Pytest:** Core test runner for executing automated unit, functional, and regression tests.
> - **Pytest-Cov (Coverage.py):** Automated code coverage measurement tool to enforce statement and branch coverage gates.
> - **Starlette TestClient:** Headless HTTP client for end-to-end REST API integration testing without spinning up external network sockets.
> - **Locust:** Open-source load and stress testing tool for simulating concurrent farmer queries and measuring server response latencies.
>
> **Test Selection Methods Applied:**
> 1. **Equivalence Partitioning (EP):** Partitioned test inputs into valid leaf images, corrupt binary byte streams, healthy leaf control samples (must trigger 0% severity and no synthetic chemicals), and out-of-range latitude/longitude coordinates ($[-90, +90], [-180, +180]$).
> 2. **Boundary Value Analysis (BVA):** Specifically targeted condition boundaries for disease severity grading ($0.0\%$ Healthy, $14.9\%$ vs. $15.0\%$ Mild/Moderate transition, $39.9\%$ vs. $40.0\%$ Moderate/Severe transition) and geospatial search radius boundaries ($0\text{ km}$, $25\text{ km}$, $100\text{ km}$).
> 3. **Concurrency Testing:** Validated inventory decrement operations under simultaneous reservation requests to prevent negative stock values."

---

### Q5: "How do you justify that this is not just a general application or ChatGPT wrapper?"
**Answer (Directly answers the notebook's 'Innovation / Justify not ChatGPT' requirement):**
> "PlantCare AI is the opposite of a generic ChatGPT wrapper for three architectural reasons:
> 1. **Physical Supply-Chain Grounding:** ChatGPT is a pure language model confined to text generation. It has zero awareness of physical retail store inventories, store coordinates, opening hours, or live stock quantities. PlantCare AI integrates physical agro-dealers into an active spatial database that supports real-time stock reservations.
> 2. **Zero-Hallucination Regulatory Compliance:** Generative LLMs are prone to hallucinating plausible-sounding but lethal chemical mixtures, incorrect dilution ratios, or banned pesticides. PlantCare AI employs a deterministic expert rule engine grounded in government-approved CIBRC standards, ensuring chemical safety and legal compliance.
> 3. **Edge Optimization vs. Expensive Cloud Calls:** Unlike a ChatGPT API wrapper that costs \$0.02 to \$0.05 per prompt and requires high-bandwidth internet connectivity, PlantCare AI uses an edge-compatible CNN model running in <80ms with zero marginal cloud API costs."

---

### Q6: "What happens if a farmer has no internet connection in the field?"
**Answer:**
> "The system is built on an **Offline-First Architecture**:
> - The MobileNetV4 model is compiled to ONNX / TensorFlow Lite and packaged directly into the mobile application. Leaf pathology classification and severity grading run completely on-device without internet access.
> - Emergency first-aid cultural measures (e.g., pruning infected foliage, isolating plots, moisture management) and standard chemical dosage information are stored in an encrypted local SQLite database.
> - When the farmer re-enters cellular coverage or reaches a village Wi-Fi hotspot, the app automatically synchronizes GPS coordinates, queries live store stock, and books a 4-hour medicine reservation."
