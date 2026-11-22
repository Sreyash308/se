# AGENT.MD: System Architecture, Engineering Standards & Agent Operational Context

> **System Name:** PlantCare AI  
> **Repository:** `/Users/harshitraj/OpenSource/se`  
> **Target Audience:** Autonomous Agents, Lead Software Architects, Senior Engineers, and Academic Reviewers  
> **Status:** Production-Ready Academic Submission & Scalable Foundation

---

## 1. System Mission & Core Domain Philosophy

PlantCare AI is engineered to bridge the **last-mile agricultural disconnect**: translating real-time computer vision plant disease detection into **immediate, verified, local agrochemical and bio-pesticide procurement**.

### The Non-Negotiable Invariants:
1. **Zero Agronomic Hallucination:** Prescriptions MUST be strictly derived from verified regulatory databases (e.g., Central Insecticides Board & Registration Committee - CIBRC / FAO standards). Chemical dosages, active ingredient percentages, and Pre-Harvest Intervals (PHI) MUST NEVER be generated dynamically by an ungrounded LLM.
2. **Deterministic Fallbacks:** If a vision model encounters out-of-distribution leaf inputs or confidence falls below `0.70`, the system MUST flag the diagnosis as uncertain and route the user to preventive biologicals and expert scouting rather than prescribing high-toxicity systemic fungicides.
3. **Spatial Efficiency:** Geospatial search must employ $O(1)$ coordinate bounding-box rejection prior to computing great-circle Haversine distances to maintain sub-150ms p95 latencies across large retailer networks.
4. **Transactional Inventory Integrity:** Reservations must be time-bounded (default: 4 hours) with atomic stock decrements to prevent overselling while smallholder farmers travel to physical retail stores.

---

## 2. Technology Stack & Architectural Patterns

```
+---------------------------------------------------------------------------------------+
|                                    ARCHITECTURE TIERS                                 |
+---------------------------------------------------------------------------------------+
|  Presentation Tier   : React PWA (Web) / Flutter (Mobile)                             |
|  API Gateway         : FastAPI (Async Python 3.10+), Pydantic v2                      |
|  Domain Logic        : Clean Architecture (Domain Services, Entities, DTOs)           |
|  Computer Vision     : PyTorch / ONNX Runtime (MobileNetV4, EfficientNet-B0)         |
|  Geospatial Engine   : PostGIS Spatial Queries, Haversine Great-Circle Engine          |
|  Persistence         : PostgreSQL (ACID relational) + Redis (Spatial Caching)         |
|  Testing & QA        : Pytest, Pytest-Cov (Coverage >= 90%), Locust (Load testing)    |
+---------------------------------------------------------------------------------------+
```

### Architectural Decisions & Rationale:
- **Modular Layered Architecture over Microservices:** Microservices introduce distributed transactions, network latency hops, and operational overhead that complicate academic evaluation and rural edge deployments. A modular layered architecture ensures clean separation of concerns with sub-millisecond in-process communication.
- **MobileNetV4 / EfficientNet-B0 over Heavy VLMs:** Heavy Vision-Language Models (e.g., 7B parameter models) require high-bandwidth cloud uplinks and cost >$0.02 per query with multi-second latencies. MobileNetV4 operates with <15MB weight footprint, <80ms edge inference, zero per-query cloud compute costs, and runs fully offline on mobile hardware.
- **Hybrid Spatial Filter (Bounding Box + Haversine):** Computing spherical trigonometric functions across thousands of database entries is CPU intensive. Bounding-box pre-filtering prunes $>92\%$ of irrelevant points using simple coordinate comparisons before applying Haversine.

---

## 3. Directory Layout & Module Responsibilities

```
se/
├── README.md                          # Public GitHub technical overview & guide (20 sections)
├── ARCH.md                            # Comprehensive System Architecture Specification
├── AGENT.md                           # This operational agent guide & architectural invariants
├── SRS.md                             # IEEE Std 830-1998 Software Requirements Specification
├── Presentation_Content/
│   ├── presentation_slides.md         # 5-Slide presentation deck matching university evaluation rubric
│   └── cross_questioning_defense.md   # Viva examination answers, SE role, and testing justifications
└── submission/
    ├── SUBMISSION_OVERVIEW.md         # Executive academic briefing & university evaluation mapping
    ├── Project_Report.md              # University academic project report (Front Matter, Ch 1-7, Back Matter)
    └── Architecture_Diagrams/
        ├── ARCHITECTURE.md            # Clean Layered Architecture & Subsystem Specifications
        ├── dfd_level_0_1_2.md         # Data Flow Diagrams (Context Level 0, Level 1, Level 2)
        ├── uml_use_case_sequence.md   # UML Use Case, Class Diagram, and Chronological Sequence Models
        └── database_erd.md            # Entity-Relationship Diagram (ERD) & PostGIS Schema
```

---

## 4. Coding Standards & Conventions

1. **Python Typings:** All functions, methods, and service signatures MUST contain strict Python type annotations (`typing.List`, `typing.Optional`, `typing.Dict`, `typing.Tuple`).
2. **Pydantic Validation:** All incoming payloads and outgoing responses must strictly adhere to Pydantic v2 models.
3. **Error Handling:** Never let unhandled 500 exceptions leak stack traces. Raise explicit `fastapi.HTTPException` with informative, sanitized error details.
4. **Immutability & Pure Functions:** Mathematical algorithms (such as Haversine and bounding-box coordinates) must remain pure static methods without side-effects.

---

## 5. Software Engineering Testing Protocols (STLC)

For academic viva defense and production readiness, testing follows strict Software Engineering principles:

### A. Test Selection Methods
- **Equivalence Partitioning (EP):** Partition inputs into:
  - Valid leaf image with clear foliar lesion.
  - Image of healthy crop (must yield 0% damage and prophylactic bio-controls only).
  - Out-of-bounds geospatial coordinates (e.g., latitude $> 90^\circ$ or $<-90^\circ$).
  - Negative search radii ($r \le 0$).
- **Boundary Value Analysis (BVA):** Severity boundaries tested at:
  - `0.0%` -> Healthy
  - `14.9%` vs `15.0%` -> Mild vs Moderate
  - `39.9%` vs `40.0%` -> Moderate vs Severe
  - Max radius: `100.0 km` boundary

### B. Defined Stop-Testing Criteria
Testing is certified complete when:
1. **100%** of all defined functional paths execute without failure.
2. **$\ge 90\%$** statement and branch code coverage across the `app/` package.
3. **Zero** open Severity-1 (Blocker) or Severity-2 (Critical) defects.
4. **Defect Density** $\le 0.1$ defects per KLOC.
5. All integration tests pass in clean environments.

---

## 6. How to Extend the Platform

### Adding a New Crop or Pathology Class:
1. Add the crop enum value to `CropType` in `app/models/entities.py`.
2. Add the pathology metadata to `DISEASE_METADATA` in `app/services/prescription_service.py` with symptoms, immediate actions, CIBRC chemical IDs, and organic alternatives.
3. Add corresponding test cases in `tests/test_diagnosis.py`.

### Adding a New Agro-Dealer Store or Inventory Integration:
1. Register store details in `STORE_CATALOG` in `app/services/agronomic_database.py`.
2. Populate initial inventory items in `INITIAL_INVENTORY` linking `store_id` and `medicine_id`.
3. If integrating an external POS / ERP database, implement the `InventoryRepository` interface in `app/services/` to replace in-memory data with PostgreSQL queries (`SELECT * FROM stores JOIN inventory ... WHERE ST_DWithin(...)`).

---

## 7. Execution Commands Quick Reference

```bash
# Run test suite with statement & branch coverage
python3 -m pytest --cov=app --cov-report=term-missing tests/

# Start API service locally
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Health check
curl http://localhost:8000/api/v1/health
```
