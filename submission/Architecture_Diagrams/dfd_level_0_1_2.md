# Data Flow Diagrams (DFD)

## 1. DFD Level 0: Context Diagram
The Level 0 context diagram defines the external boundaries, primary actors, and overarching data flows of PlantCare AI.

```mermaid
flowchart LR
    Farmer(["Smallholder Farmer"])
    Dealer(["Agro-Dealer Retailer"])
    System[["PlantCare AI System"]]
    Admin(["System Administrator"])

    Farmer -->|"Leaf Image, Crop Type, GPS Coords"| System
    System -->|"Diagnosis, Severity, Prescription, Store List, Pickup Code"| Farmer

    Dealer -->|"Stock Updates, Medicine Pricing, Hours"| System
    System -->|"Reservation Notices, Pickup Verification"| Dealer

    Admin -->|"Regulatory Updates (CIBRC), User Governance"| System
    System -->|"System Telemetry, Audit Logs"| Admin
```

---

## 2. DFD Level 1: Major Functional Processes
The Level 1 diagram decomposes the system into four core functional processes and four primary data stores.

```mermaid
flowchart TD
    Farmer(["Farmer / User"])
    Dealer(["Agro-Dealer Retailer"])

    P1["1.0 Image Ingestion & Validation"]
    P2["2.0 Neural Pathology Inference & Severity"]
    P3["3.0 Agronomic Prescription Formulation"]
    P4["4.0 Spatial Search & Stock Reservation"]

    D1[("D1: Image & Telemetry Buffer")]
    D2[("D2: Model Weights & Pathology Metadata")]
    D3[("D3: CIBRC Medicine Catalog")]
    D4[("D4: Agro-Store & Inventory Database")]

    Farmer -->|"Raw Image + GPS"| P1
    P1 -->|"Validated Tensor"| D1
    D1 -->|"Tensor"| P2

    P2 <-->|"Feature Maps & Classes"| D2
    P2 -->|"Pathology + Severity %"| P3

    P3 <-->|"Regulatory Guidelines & Dosage"| D3
    P3 -->|"Target Medicine IDs + GPS"| P4

    Dealer -->|"Live Stock & Price Feeds"| D4
    P4 <-->|"Spatial Query & Inventory Locks"| D4

    P4 -->|"Prescription + Nearest Stores + Pickup Code"| Farmer
```

---

## 3. DFD Level 2: Decomposed Spatial & Reservation Engine (Process 4.0)
Decomposition of Process 4.0 illustrating bounding-box pre-filtering, Haversine geodesic calculation, inventory joining, and atomic reservation locking.

```mermaid
flowchart TD
    InputData["Input: Farmer (lat, lon), Radius (km), Target Med IDs"]
    
    P4_1["4.1 Bounding-Box Coordinate Filter"]
    P4_2["4.2 Haversine Geodesic Distance Engine"]
    P4_3["4.3 Relational Inventory & Stock Join"]
    P4_4["4.4 Proximity & Pricing Rank Sort"]
    P4_5["4.5 Atomic Reservation & Token Issuance"]

    StoreTable[("Agro-Dealer Table")]
    InvTable[("Inventory Stock Table")]
    ResTable[("Reservation Ledger")]

    InputData --> P4_1
    StoreTable -->|"All Registered Coordinates"| P4_1
    P4_1 -->|"Pruned Candidate Store IDs (<8% of total)"| P4_2
    
    P4_2 -->|"Exact Distance (km) & Driving Time"| P4_3
    InvTable -->|"Live Stock Count & Price"| P4_3

    P4_3 -->|"In-Stock Store Candidates"| P4_4
    P4_4 -->|"Ranked Nearby Store List"| OutputToUser["Output to Farmer Screen"]

    OutputToUser -.->|"Farmer Initiates Hold"| P4_5
    P4_5 -->|"Atomic Decrement"| InvTable
    P4_5 -->|"Create Reservation Record"| ResTable
    P4_5 -->|"Issue Pickup Code (PK-XXXXXX)"| Confirmation["Reservation Confirmed Screen"]
```
