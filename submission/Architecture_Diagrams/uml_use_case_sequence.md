# UML Diagrams: Use Case, Class, and Sequence Models

## 1. Use Case Diagram
Illustrates the actor interactions and system boundary use cases for Farmers, Agro-Dealers, and Agronomist Admins.

```mermaid
flowchart LR
    Farmer(("Smallholder Farmer"))
    Dealer(("Agro-Dealer"))
    Admin(("Agronomist Admin"))

    subgraph PlantCare_AI_Boundary ["PlantCare AI System Boundary"]
        UC1(["UC-1: Capture / Upload Leaf Image"])
        UC2(["UC-2: View Disease Diagnosis & Severity"])
        UC3(["UC-3: View Dual Prescriptions (Chemical & Organic)"])
        UC4(["UC-4: Search Nearby In-Stock Agro-Stores"])
        UC5(["UC-5: Reserve Medicine with Pickup Code"])
        UC6(["UC-6: Update Store Inventory & Prices"])
        UC7(["UC-7: Verify Pickup Code & Fulfill Reservation"])
        UC8(["UC-8: Maintain CIBRC Regulatory Catalog"])
    end

    Farmer --> UC1
    Farmer --> UC2
    Farmer --> UC3
    Farmer --> UC4
    Farmer --> UC5

    Dealer --> UC6
    Dealer --> UC7

    Admin --> UC8
    UC2 -.->|<<includes>>| UC1
    UC3 -.->|<<includes>>| UC2
    UC4 -.->|<<extends>>| UC3
    UC5 -.->|<<extends>>| UC4
```

---

## 2. UML Class Diagram
Defines the object-oriented structure, class relationships, attributes, and public interface methods.

```mermaid
classDiagram
    class DiagnosisService {
        -float confidence_threshold
        +diagnose_image(bytes image_bytes, str crop_hint) DiagnosisResult
        -preprocess_image(bytes raw_bytes) Tensor
        -estimate_severity(Tensor lesion_mask) DiseaseSeverity
    }

    class PrescriptionService {
        +get_prescription(str disease_key, DiseaseSeverity severity) Dict
        -validate_cibrc_compliance(str medicine_id) bool
    }

    class SpatialInventoryService {
        +float EARTH_RADIUS_KM
        -dict stores
        -dict medicines
        -list inventory
        +haversine_distance(float lat1, float lon1, float lat2, float lon2) float
        +find_nearby_medicines(float lat, float lon, list med_ids, float radius) List~StoreAvailabilityResult~
        +create_reservation(str farmer_name, str store_id, str med_id, int qty) Dict
    }

    class Medicine {
        +str id
        +str name
        +str active_ingredient
        +str concentration
        +MedicineType medicine_type
        +str dosage_per_acre
        +str dilution_instructions
        +bool is_organic
        +int safety_waiting_period_days
    }

    class Store {
        +str id
        +str name
        +str license_number
        +str phone
        +float latitude
        +float longitude
        +bool is_verified
    }

    class InventoryItem {
        +str id
        +str store_id
        +str medicine_id
        +int stock_quantity_units
        +float price_inr
        +bool is_in_stock
        +str last_updated
    }

    class DiagnosisResult {
        +str crop
        +str disease_name
        +float confidence_score
        +DiseaseSeverity severity
        +float affected_percentage
        +List~Medicine~ chemical_treatments
        +List~Medicine~ organic_treatments
    }

    DiagnosisService ..> PrescriptionService : invokes
    PrescriptionService ..> Medicine : references
    SpatialInventoryService --> Store : manages
    SpatialInventoryService --> InventoryItem : queries
    SpatialInventoryService ..> Medicine : resolves
    DiagnosisService ..> DiagnosisResult : returns
    InventoryItem --> Store : belongs_to
    InventoryItem --> Medicine : tracks_stock_of
```

---

## 3. UML Sequence Diagram: End-to-End User Flow
Illustrates the chronological message flow from initial leaf capture to physical inventory reservation.

```mermaid
sequenceDiagram
    autonumber
    actor Farmer as Smallholder Farmer
    participant App as Mobile Client
    participant API as FastAPI Gateway
    participant Diag as DiagnosisService
    participant Presc as PrescriptionService
    participant Spatial as SpatialInventoryService
    participant DB as PostGIS / Inventory DB

    Farmer->>App: Capture leaf photo & grant GPS location
    App->>API: POST /api/v1/diagnose (image_bytes, crop="Tomato", GPS)
    
    API->>Diag: diagnose_image(image_bytes, "Tomato")
    Diag->>Diag: Resize to 224x224, run CNN inference
    Diag->>Diag: Segment lesion area -> 28.4% (Moderate)
    Diag->>Presc: get_prescription("Tomato___Early_blight", MODERATE)
    Presc-->>Diag: Return chemical (Mancozeb) & bio (Trichoderma)
    Diag-->>API: Return DiagnosisResult
    API-->>App: Display diagnosis, severity & treatment options

    Farmer->>App: Tap "Find Nearby In-Stock Medicine"
    App->>API: POST /api/v1/medicines/nearby (med_id="MED-MCZ-75", lat, lon, radius=25km)
    API->>Spatial: find_nearby_medicines(lat, lon, ["MED-MCZ-75"], 25km)
    Spatial->>DB: Query stores within bounding box [lat ± Δ, lon ± Δ]
    DB-->>Spatial: Return 3 candidate stores
    Spatial->>Spatial: Compute exact Haversine distance
    Spatial->>DB: Check live inventory & prices
    DB-->>Spatial: STR-001 has 42 units in stock @ Rs 320
    Spatial-->>API: Return List[StoreAvailabilityResult] (Sorted by proximity)
    API-->>App: Render map & store list (Kisan Agro Kendra, 2.8 km away)

    Farmer->>App: Tap "Reserve 2 Units (4-Hr Hold)"
    App->>API: POST /api/v1/medicines/reserve (store_id, med_id, qty=2)
    API->>Spatial: create_reservation("Ramesh", STR-001, MED-MCZ-75, 2)
    Spatial->>DB: Atomic decrement: stock 42 -> 40
    Spatial-->>API: Reservation Confirmed (Code: PK-E38B12, Expiry: 4 hrs)
    API-->>App: Display Pickup Voucher with QR / Code
    Farmer->>App: Show pickup code at store counter for instant collection
```
