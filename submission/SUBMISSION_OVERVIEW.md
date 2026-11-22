# Academic Project Submission Dossier
## PlantCare AI: Disease Diagnosis & Nearby Plant Medicine Availability

**Course:** Software Engineering (SE) Academic Capstone / Major Project  
**Candidate Name:** Harshit Raj  
**Registration / Roll No:** 2023-CS-0891  
**Department:** Computer Science & Engineering  
**Submission Deadline:** November 25, 2026  
**Evaluation Dates:** Starting November 25, 2026 (Viva & Cross-Questioning Defense)

---

## 1. Submission Package Contents

This `submission/` package constitutes a university-level submission complying with both academic project guidelines and industry engineering standards:

```
submission/
├── SUBMISSION_OVERVIEW.md         # Executive submission briefing & evaluation mapping
├── Project_Report.md              # Complete Academic Project Report (Front Matter, Ch 1-7, References)
└── Architecture_Diagrams/
    ├── ARCHITECTURE.md            # Clean Layered Architecture & Subsystem Specifications
    ├── dfd_level_0_1_2.md         # Data Flow Diagrams (Context Level 0, Level 1, Level 2)
    ├── uml_use_case_sequence.md   # UML Use Case, Class Diagram, and Chronological Sequence Models
    └── database_erd.md            # Entity-Relationship Diagram (ERD) & PostGIS Schema
```

---

## 2. University Evaluation Rubric Compliance

This submission addresses every requirement outlined in the academic evaluation notes:

| Academic Evaluation Requirement | How & Where PlantCare AI Addresses It | Supporting Section |
| :--- | :--- | :--- |
| **Pinpoint the Problem Solved** | Solves the **Last-Mile Agricultural Procurement Disconnect**: the physical delay and failure to procure verified remedies within the 48-72h pathogen survival window. | `Project_Report.md` Section 1.2<br>`Presentation_Content/presentation_slides.md` Slide 1 |
| **Role of Software Engineering (SE)** | Translates isolated deep learning into a production-grade distributed architecture (Clean Layered Architecture, Domain-Driven Design, PostGIS Spatial R-Tree, atomic state-locking for reservations). | `Project_Report.md` Chapter 4<br>`Presentation_Content/presentation_slides.md` Slide 3 |
| **Why That Approach? (Engineering Trade-Offs)** | Explicitly justifies design choices over alternatives: PostGIS Bounding-Box + Haversine vs. Brute-Force $O(N)$ / Google API; MobileNetV4 Edge CNN vs. Heavy Cloud VLMs; Layered Monolith vs. Microservices. | `Project_Report.md` Section 5.1<br>`Presentation_Content/presentation_slides.md` Slide 4 |
| **Significant Outcomes & Results** | 96.4% top-1 diagnostic accuracy across 38 crop-disease categories; 89.4% reduction in farmer turnaround time (from 36 hours down to 3.8 hours); sub-150ms spatial query latency. | `Project_Report.md` Chapter 6<br>`Presentation_Content/presentation_slides.md` Slide 5 |
| **Innovation / Justify Not ChatGPT** | ChatGPT produces ungrounded text and hallucinations without awareness of physical store stock. PlantCare AI integrates physical agricultural retailers, live inventory verification, and deterministic CIBRC-compliant prescriptions. | `Project_Report.md` Section 2.4<br>`Presentation_Content/presentation_slides.md` Slide 5 |
| **When to Stop Software Testing (ST)** | 5 defined quantifiable criteria: 100% test execution, $\ge 90\%$ statement coverage, $\ge 85\%$ branch coverage, 0 open P0/P1 defects, and Defect Density $\le 0.1$ defects/KLOC. | `Project_Report.md` Section 6.3<br>`Presentation_Content/cross_questioning_defense.md` Q3 |
| **What Tools to Use for STT (Selection Methods)** | Pytest, Pytest-Cov, Locust, Starlette TestClient. Selection methods: Equivalence Partitioning (EP), Boundary Value Analysis (BVA), and concurrency race condition testing. | `Project_Report.md` Section 6.1<br>`Presentation_Content/cross_questioning_defense.md` Q4 |
| **Presentation Constraints (5 Slides Max)** | Custom 5-slide deck structured for the 10-minute presentation with zero extraneous slides, paired with a comprehensive viva defense guide. | `Presentation_Content/presentation_slides.md` |

---

## 3. Key Contact Information

- **Student Researcher:** Harshit Raj
- **Project Repository:** `https://github.com/harshitraj1236/se`
- **Documentation Master:** `README.md`
- **System Architecture:** `ARCH.md`
- **Requirements Specification:** `SRS.md`
- **System Agent Instructions:** `AGENT.md`
