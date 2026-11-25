"""
Agronomic Database and Knowledge Base.
Contains regulatory CIBRC-approved formulations, disease pathology profiles,
agro-dealer store locations, and initial inventory ledgers.
"""

from typing import Dict, List
from app.models.entities import (
    CropType,
    PathogenType,
    MedicineItem,
    DiseasePathology,
    StoreEntity,
    InventoryRecord,
)

# ---------------------------------------------------------------------------
# 1. CIBRC Approved Formulations (Chemical & Certified Bio-Control)
# ---------------------------------------------------------------------------

MEDICINES_CATALOG: Dict[str, MedicineItem] = {
    "MED-MCZ-75": MedicineItem(
        id="MED-MCZ-75",
        name="Mancozeb 75% WP",
        active_ingredient="Mancozeb",
        concentration="75% Wettable Powder",
        is_organic=False,
        dosage_per_acre="600-800 grams",
        dilution_instructions="Dissolve 2.0-2.5g in 1 liter of clean water (approx. 300-400L spray solution per acre).",
        safety_waiting_period_days=7,
        regulatory_cibrc_approved=True,
        target_pathogens=["Early Blight", "Late Blight", "Apple Scab", "Common Rust"],
    ),
    "MED-CPX-50": MedicineItem(
        id="MED-CPX-50",
        name="Copper Oxychloride 50% WP",
        active_ingredient="Copper Oxychloride",
        concentration="50% Wettable Powder",
        is_organic=False,
        dosage_per_acre="1000-1200 grams",
        dilution_instructions="Mix 2.5-3.0g per liter of water. Ensure thorough foliar coverage under leaves.",
        safety_waiting_period_days=14,
        regulatory_cibrc_approved=True,
        target_pathogens=["Bacterial Spot", "Early Blight", "Late Blight", "Cercospora Leaf Spot"],
    ),
    "MED-AZX-23": MedicineItem(
        id="MED-AZX-23",
        name="Azoxystrobin 23% SC",
        active_ingredient="Azoxystrobin",
        concentration="23% Suspension Concentrate",
        is_organic=False,
        dosage_per_acre="200 milliliters",
        dilution_instructions="Mix 1.0ml per liter of water. Apply at first sign of sporulation.",
        safety_waiting_period_days=5,
        regulatory_cibrc_approved=True,
        target_pathogens=["Late Blight", "Sheath Blight", "Powdery Mildew", "Black Rot"],
    ),
    "MED-MTX-MZ": MedicineItem(
        id="MED-MTX-MZ",
        name="Metalaxyl 8% + Mancozeb 64% WP",
        active_ingredient="Metalaxyl + Mancozeb",
        concentration="72% Wettable Powder",
        is_organic=False,
        dosage_per_acre="600-750 grams",
        dilution_instructions="Dissolve 2.0g per liter of water. Dual action: systemic absorption + surface protective shield.",
        safety_waiting_period_days=10,
        regulatory_cibrc_approved=True,
        target_pathogens=["Late Blight", "Downy Mildew", "Damping Off"],
    ),
    "MED-HEX-05": MedicineItem(
        id="MED-HEX-05",
        name="Hexaconazole 5% SC",
        active_ingredient="Hexaconazole",
        concentration="5% Suspension Concentrate",
        is_organic=False,
        dosage_per_acre="400 milliliters",
        dilution_instructions="Mix 2.0ml per liter of water. Systemic triazole eradicant.",
        safety_waiting_period_days=15,
        regulatory_cibrc_approved=True,
        target_pathogens=["Powdery Mildew", "Sheath Blight", "Apple Scab", "Rust"],
    ),
    "MED-STR-09": MedicineItem(
        id="MED-STR-09",
        name="Streptomycin Sulphate 9% + Tetracycline Hydrochloride 1% SP",
        active_ingredient="Streptomycin + Tetracycline",
        concentration="10% Soluble Powder",
        is_organic=False,
        dosage_per_acre="40-50 grams",
        dilution_instructions="Dissolve 6g per 60 liters of water (approx. 0.1-0.2g per liter). Enforce mask PPE.",
        safety_waiting_period_days=14,
        regulatory_cibrc_approved=True,
        target_pathogens=["Bacterial Spot", "Bacterial Leaf Blight", "Bacterial Canker"],
    ),
    "MED-VAL-03": MedicineItem(
        id="MED-VAL-03",
        name="Validamycin 3% L",
        active_ingredient="Validamycin",
        concentration="3% Liquid",
        is_organic=False,
        dosage_per_acre="1000 milliliters",
        dilution_instructions="Mix 2.5ml per liter of clean water. Direct spray to crop base and leaf sheaths.",
        safety_waiting_period_days=14,
        regulatory_cibrc_approved=True,
        target_pathogens=["Sheath Blight", "Stem Rot"],
    ),
    "MED-PRO-25": MedicineItem(
        id="MED-PRO-25",
        name="Propiconazole 25% EC",
        active_ingredient="Propiconazole",
        concentration="25% Emulsifiable Concentrate",
        is_organic=False,
        dosage_per_acre="200 milliliters",
        dilution_instructions="Mix 1.0ml per liter of water. Do not apply during flowering to preserve honeybees.",
        safety_waiting_period_days=21,
        regulatory_cibrc_approved=True,
        target_pathogens=["Northern Leaf Blight", "Common Rust", "Rice Blast"],
    ),
    "MED-TRI-VIR": MedicineItem(
        id="MED-TRI-VIR",
        name="Trichoderma viride 1% WP",
        active_ingredient="Trichoderma viride (CFU 2x10^6/g)",
        concentration="1% Wettable Powder (Certified Bio-Fungicide)",
        is_organic=True,
        dosage_per_acre="1000 grams",
        dilution_instructions="Mix 5.0g per liter of clean chlorine-free water. Can also be mixed with 50kg farmyard manure.",
        safety_waiting_period_days=0,
        regulatory_cibrc_approved=True,
        target_pathogens=["Early Blight", "Late Blight", "Sheath Blight", "Root Rot"],
    ),
    "MED-BAC-SUB": MedicineItem(
        id="MED-BAC-SUB",
        name="Bacillus subtilis 2% AS",
        active_ingredient="Bacillus subtilis (CFU 1x10^9/ml)",
        concentration="2% Aqueous Suspension (Bio-Control)",
        is_organic=True,
        dosage_per_acre="500-600 milliliters",
        dilution_instructions="Mix 2.5ml per liter of water. Colonizes plant foliar surfaces to antagonize fungal hyphae.",
        safety_waiting_period_days=0,
        regulatory_cibrc_approved=True,
        target_pathogens=["Bacterial Spot", "Early Blight", "Powdery Mildew"],
    ),
    "MED-AZA-10": MedicineItem(
        id="MED-AZA-10",
        name="Azadirachtin 10,000 PPM (Neem Bio-Pesticide)",
        active_ingredient="Azadirachtin",
        concentration="1.0% EC Neem Formulation",
        is_organic=True,
        dosage_per_acre="400-500 milliliters",
        dilution_instructions="Dilute 2.0ml per liter of water with 0.5ml mild surfactant. Spray during cool morning/evening hours.",
        safety_waiting_period_days=3,
        regulatory_cibrc_approved=True,
        target_pathogens=["Whitefly Vector", "Early Blight", "Aphids", "Mild Fungal Colonization"],
    ),
    "MED-PSE-FLU": MedicineItem(
        id="MED-PSE-FLU",
        name="Pseudomonas fluorescens 1% WP",
        active_ingredient="Pseudomonas fluorescens (CFU 2x10^8/g)",
        concentration="1% Bio-Bactericide / Antagonist",
        is_organic=True,
        dosage_per_acre="1000 grams",
        dilution_instructions="Dissolve 5.0g per liter of water. Induces systemic acquired resistance (SAR) in plants.",
        safety_waiting_period_days=0,
        regulatory_cibrc_approved=True,
        target_pathogens=["Bacterial Spot", "Bacterial Wilt", "Blast"],
    ),
    "MED-SUL-80": MedicineItem(
        id="MED-SUL-80",
        name="Wettable Sulphur 80% WDG",
        active_ingredient="Elemental Sulphur",
        concentration="80% Water Dispersible Granules",
        is_organic=True,
        dosage_per_acre="1000 grams",
        dilution_instructions="Dissolve 2.5-3.0g per liter of water. Avoid application if ambient temperature exceeds 32°C.",
        safety_waiting_period_days=3,
        regulatory_cibrc_approved=True,
        target_pathogens=["Powdery Mildew", "Rust", "Mites"],
    ),
    "MED-BIO-NIL": MedicineItem(
        id="MED-BIO-NIL",
        name="Prophylactic Seaweed Bio-Stimulant + Zinc Chelate",
        active_ingredient="Ascophyllum nodosum extract + Zn-EDTA 12%",
        concentration="Standard Agricultural Grade",
        is_organic=True,
        dosage_per_acre="500 milliliters",
        dilution_instructions="Dilute 2.0ml per liter of water. Fortifies foliar cuticle and stimulates natural plant phytoalexins.",
        safety_waiting_period_days=0,
        regulatory_cibrc_approved=True,
        target_pathogens=["Preventive Foliar Tonic / Healthy Canopy"],
    ),
}

# ---------------------------------------------------------------------------
# 2. Comprehensive Crop Pathology Catalog
# ---------------------------------------------------------------------------

DISEASE_CATALOG: Dict[str, DiseasePathology] = {
    # TOMATO PATHOLOGIES
    "TOMATO_EARLY_BLIGHT": DiseasePathology(
        disease_id="TOMATO_EARLY_BLIGHT",
        crop=CropType.TOMATO,
        common_name="Early Blight",
        scientific_name="Alternaria solani",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Concentric ring dark brown spots (target-board pattern) on older lower leaves",
            "Yellow halo chlorosis surrounding necrotic leaf spots",
            "Progressive foliar defoliation advancing from base upward",
            "Sunscald vulnerability on exposed ripening fruit"
        ],
        immediate_actions=[
            "Immediately prune and safely destroy infected lower leaves (do not compost).",
            "Avoid overhead sprinkler irrigation to keep the canopy dry.",
            "Sanitize pruning shears with 70% isopropyl alcohol between plants."
        ],
        chemical_medicine_ids=["MED-MCZ-75", "MED-CPX-50"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-AZA-10"],
        preventive_measures=[
            "Implement a minimum 3-year crop rotation with non-solanaceous crops.",
            "Apply straw mulch to prevent soil-splash inoculum onto lower foliage.",
            "Maintain wide 60cm row spacing for rapid morning leaf drying."
        ],
    ),
    "TOMATO_LATE_BLIGHT": DiseasePathology(
        disease_id="TOMATO_LATE_BLIGHT",
        crop=CropType.TOMATO,
        common_name="Late Blight",
        scientific_name="Phytophthora infestans",
        pathogen_type=PathogenType.FUNGAL_OOMYCOTA,
        key_symptoms=[
            "Water-soaked pale to dark olive lesions rapidly enlarging across leaves",
            "Delicate white downy fungal mildew on leaf undersides under high humidity (>90%)",
            "Rapid stem collapse and foul-smelling dark brown fruit decay",
            "Destruction of entire field canopies within 72 to 96 hours"
        ],
        immediate_actions=[
            "Halt all overhead watering immediately.",
            "Scout perimeter rows and rogue out severely infected plants in sealed bags.",
            "Execute targeted systemic fungicide spray within 24 hours of first lesion detection."
        ],
        chemical_medicine_ids=["MED-MTX-MZ", "MED-AZX-23"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=[
            "Plant certified disease-free, resistant hybrid cultivars.",
            "Ensure field soil has adequate drainage to prevent waterlogging.",
            "Monitor regional late blight forecasting warnings during cool rainy periods."
        ],
    ),
    "TOMATO_BACTERIAL_SPOT": DiseasePathology(
        disease_id="TOMATO_BACTERIAL_SPOT",
        crop=CropType.TOMATO,
        common_name="Bacterial Spot",
        scientific_name="Xanthomonas perforans",
        pathogen_type=PathogenType.BACTERIAL,
        key_symptoms=[
            "Small (2-3mm) circular water-soaked dark brown spots with translucent margins",
            "Shot-hole appearance as necrotic leaf centers dry and tear out",
            "Raised blister-like scabby spots on green and ripe tomato fruit"
        ],
        immediate_actions=[
            "Never work or cultivate in the field while foliage is wet from dew or rain.",
            "Prune infected plant terminals with clean sterilized tools.",
            "Apply protective copper-bactericide tank mix."
        ],
        chemical_medicine_ids=["MED-CPX-50", "MED-STR-09"],
        organic_medicine_ids=["MED-PSE-FLU", "MED-BAC-SUB"],
        preventive_measures=[
            "Utilize certified hot-water treated pathogen-free seeds.",
            "Avoid handling foliage when wet to arrest mechanical vector transmission.",
            "Eradicate solanaceous weed hosts (black nightshade) around field boundaries."
        ],
    ),
    "TOMATO_HEALTHY": DiseasePathology(
        disease_id="TOMATO_HEALTHY",
        crop=CropType.TOMATO,
        common_name="Healthy Tomato Canopy",
        scientific_name="Lycopersicon esculentum (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=[
            "Vibrant, turgid, uniformly green foliar canopy",
            "Zero necrotic lesions, chlorotic halos, or pathogen sporulation",
            "Normal reproductive flower development and vigorous terminal shoot growth"
        ],
        immediate_actions=[
            "Maintain balanced N-P-K fertigation; do not apply synthetic chemical fungicides.",
            "Maintain scouting records twice weekly during early morning inspections."
        ],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=[
            "Apply prophylactic bio-stimulant or neem preventative tonic every 14 days.",
            "Ensure steady drip irrigation scheduling to prevent blossom end rot."
        ],
    ),

    # POTATO PATHOLOGIES
    "POTATO_EARLY_BLIGHT": DiseasePathology(
        disease_id="POTATO_EARLY_BLIGHT",
        crop=CropType.POTATO,
        common_name="Early Blight",
        scientific_name="Alternaria solani",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Small brownish-black spots on older potato leaves showing target-like concentric rings",
            "Yellowing tissue margins around lesions causing premature senescence",
            "Shallow, dark, sunken lesions on potato tuber surfaces"
        ],
        immediate_actions=[
            "Destroy infected senescent haulms immediately.",
            "Spray protective contact fungicide to preserve top canopy photosynthetic area."
        ],
        chemical_medicine_ids=["MED-MCZ-75", "MED-CPX-50"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-AZA-10"],
        preventive_measures=[
            "Ensure balanced potassium and nitrogen nutrition to avoid premature vine stress.",
            "Practice certified 2-to-3-year rotation away from potato, tomato, and eggplant."
        ],
    ),
    "POTATO_LATE_BLIGHT": DiseasePathology(
        disease_id="POTATO_LATE_BLIGHT",
        crop=CropType.POTATO,
        common_name="Late Blight",
        scientific_name="Phytophthora infestans",
        pathogen_type=PathogenType.FUNGAL_OOMYCOTA,
        key_symptoms=[
            "Irregular water-soaked brown lesions on leaf tips and leaf margins",
            "White fungal growth on the underside of foliage in moist morning conditions",
            "Brownish-purple granular dry rot in stored or harvested tubers",
            "Total foliage collapse in under 5 days during persistent overcast weather"
        ],
        immediate_actions=[
            "Apply combination systemic + contact curative fungicide within 24 hours.",
            "Kill haulms (vine desiccation) 14 days prior to harvest if infection reaches stem."
        ],
        chemical_medicine_ids=["MED-MTX-MZ", "MED-AZX-23"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=[
            "Plant certified seed tubers certified free from latent Phytophthora.",
            "Hill up ridges firmly with soil to create a minimum 10cm barrier over tubers."
        ],
    ),
    "POTATO_HEALTHY": DiseasePathology(
        disease_id="POTATO_HEALTHY",
        crop=CropType.POTATO,
        common_name="Healthy Potato Foliage",
        scientific_name="Solanum tuberosum (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=[
            "Healthy deep green leaves, sturdy haulms, absence of leaf spotting"
        ],
        immediate_actions=[
            "Continue standard agronomic monitoring and balanced irrigation."
        ],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=[
            "Routine preventive bio-tonic application; maintain good soil hilling."
        ],
    ),

    # CORN PATHOLOGIES
    "CORN_COMMON_RUST": DiseasePathology(
        disease_id="CORN_COMMON_RUST",
        crop=CropType.CORN,
        common_name="Common Rust",
        scientific_name="Puccinia sorghi",
        pathogen_type=PathogenType.FUNGAL_BASIDIOMYCOTA,
        key_symptoms=[
            "Golden-brown to cinnamon powdery pustules (uredinia) on upper and lower leaf surfaces",
            "Pustules rupture epidermal tissue, releasing rust-colored airborne spores",
            "Chlorosis and premature leaf death on heavily infected lower leaves"
        ],
        immediate_actions=[
            "Assess threshold: if rust covers >10% of ear leaf area before tasseling, spray fungicide.",
            "Avoid nitrogen overload which creates lush, highly susceptible foliar tissue."
        ],
        chemical_medicine_ids=["MED-PRO-25", "MED-HEX-05"],
        organic_medicine_ids=["MED-SUL-80", "MED-AZA-10"],
        preventive_measures=[
            "Plant rust-resistant commercial maize hybrids.",
            "Early planting to avoid mid-season spore transport from southern corridors."
        ],
    ),
    "CORN_NORTHERN_BLIGHT": DiseasePathology(
        disease_id="CORN_NORTHERN_BLIGHT",
        crop=CropType.CORN,
        common_name="Northern Leaf Blight",
        scientific_name="Exserohilum turcicum",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Elongated cigar-shaped grayish-green to tan lesions (2.5 to 15cm long)",
            "Lesions develop dark olive fungal sporulation in damp conditions",
            "Blended lesions creating extensive foliar burning and premature dry-down"
        ],
        immediate_actions=[
            "Apply systemic triazole/strobilurin fungicide prior to silking stage."
        ],
        chemical_medicine_ids=["MED-PRO-25", "MED-AZX-23"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=[
            "Deep tillage to bury infected maize crop debris where fungal spores overwinter.",
            "Rotate fields with soybean, pulses, or wheat for at least one season."
        ],
    ),
    "CORN_HEALTHY": DiseasePathology(
        disease_id="CORN_HEALTHY",
        crop=CropType.CORN,
        common_name="Healthy Corn Crop",
        scientific_name="Zea mays (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Broad, upright, dark green leaves with uniform venation and no pustules."],
        immediate_actions=["Maintain scheduled sidedress nitrogen and adequate soil moisture."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Scout field every 7 days; maintain weed-free crop rows."],
    ),

    # APPLE PATHOLOGIES
    "APPLE_SCAB": DiseasePathology(
        disease_id="APPLE_SCAB",
        crop=CropType.APPLE,
        common_name="Apple Scab",
        scientific_name="Venturia inaequalis",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Olive-green velvety spots on leaves that turn brownish-black and corky",
            "Curled, twisted leaf margins followed by early defoliation",
            "Cracked, scabbed, stunted fruit unmarketable for commercial sale"
        ],
        immediate_actions=[
            "Rake and shred or compost fallen orchard leaves to eliminate primary pseudothecia.",
            "Apply protective fungicide before predicted rain infection periods."
        ],
        chemical_medicine_ids=["MED-MCZ-75", "MED-HEX-05"],
        organic_medicine_ids=["MED-SUL-80", "MED-BAC-SUB"],
        preventive_measures=[
            "Prune tree canopy annually to facilitate sunlight penetration and rapid air drying.",
            "Spray orchard floor with 5% agricultural urea in late autumn to accelerate leaf decay."
        ],
    ),
    "APPLE_HEALTHY": DiseasePathology(
        disease_id="APPLE_HEALTHY",
        crop=CropType.APPLE,
        common_name="Healthy Apple Foliage",
        scientific_name="Malus domestica (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Bright glossy green foliage with clean spurs and developing fruitlets."],
        immediate_actions=["Maintain orchard nutrition and tree pruning."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Routine dormant oil spray in winter; regular orchard scouting."],
    ),

    # GRAPE PATHOLOGIES
    "GRAPE_BLACK_ROT": DiseasePathology(
        disease_id="GRAPE_BLACK_ROT",
        crop=CropType.GRAPE,
        common_name="Grape Black Rot",
        scientific_name="Guignardia bidwellii",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Reddish-brown circular spots on leaves with tiny black fruiting bodies (pycnidia)",
            "Infected berries shrivel into hard, black, wrinkled mummies in clusters"
        ],
        immediate_actions=[
            "Hand-pick and remove mummified grape clusters and burn or bury deeply.",
            "Apply systemic protective fungicide spray immediately after bloom."
        ],
        chemical_medicine_ids=["MED-AZX-23", "MED-MCZ-75"],
        organic_medicine_ids=["MED-SUL-80", "MED-BAC-SUB"],
        preventive_measures=[
            "Maintain trellis canopy management to maximize air circulation through bunches.",
            "Remove all wild Vitis vines within 500 meters of commercial vineyard."
        ],
    ),
    "GRAPE_HEALTHY": DiseasePathology(
        disease_id="GRAPE_HEALTHY",
        crop=CropType.GRAPE,
        common_name="Healthy Grape Vine",
        scientific_name="Vitis vinifera (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Lush green grape leaves without necrotic spots or powdery film."],
        immediate_actions=["Maintain canopy shoot thinning and balanced potassium fertigation."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Monitor weather humidity; apply organic sulphur preventative spray."],
    ),

    # RICE PATHOLOGIES
    "RICE_BLAST": DiseasePathology(
        disease_id="RICE_BLAST",
        crop=CropType.RICE,
        common_name="Rice Blast",
        scientific_name="Magnaporthe oryzae",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Spindle-shaped (diamond-shaped) lesions with gray-white centers and dark brown margins",
            "Lesions coalesce, causing entire leaf blades to wither and dry (leaf blast)",
            "Rotting and snapping of the panicle neck node resulting in completely empty grains (neck blast)"
        ],
        immediate_actions=[
            "Avoid excessive split-dose chemical nitrogen applications immediately.",
            "Maintain continuous shallow field flooding (5cm) to suppress conidial germination.",
            "Apply curative systemic triazole/antibiotic fungicide."
        ],
        chemical_medicine_ids=["MED-PRO-25", "MED-HEX-05"],
        organic_medicine_ids=["MED-PSE-FLU", "MED-TRI-VIR"],
        preventive_measures=[
            "Treat paddy seeds with bio-agent or recommended formulation prior to nursery sowing.",
            "Avoid late planting and use blast-resistant high-yielding varieties."
        ],
    ),
    "RICE_SHEATH_BLIGHT": DiseasePathology(
        disease_id="RICE_SHEATH_BLIGHT",
        crop=CropType.RICE,
        common_name="Rice Sheath Blight",
        scientific_name="Rhizoctonia solani",
        pathogen_type=PathogenType.FUNGAL_BASIDIOMYCOTA,
        key_symptoms=[
            "Greenish-gray water-soaked oval spots on leaf sheaths near water line",
            "Spots enlarge with irregular borders resembling snake-skin patterns",
            "Lodging of rice tillers under dense field planting conditions"
        ],
        immediate_actions=[
            "Drain excess stagnant field water for 3 to 4 days to aerate the root zone.",
            "Direct targeted spray to bottom leaf sheaths using Validamycin."
        ],
        chemical_medicine_ids=["MED-VAL-03", "MED-HEX-05"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-PSE-FLU"],
        preventive_measures=[
            "Avoid overly high seedling density (maintain 20cm x 15cm hill spacing).",
            "Apply potash in split applications to harden culm and leaf sheath tissues."
        ],
    ),
    "RICE_HEALTHY": DiseasePathology(
        disease_id="RICE_HEALTHY",
        crop=CropType.RICE,
        common_name="Healthy Rice Paddy",
        scientific_name="Oryza sativa (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Uniform green tillers, healthy erect flag leaves, no water-soaked sheath lesions."],
        immediate_actions=["Maintain regular alternate wetting and drying (AWD) water management."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Monitor pest populations (BPH); maintain clean bunds."],
    ),
    "RICE_BROWN_SPOT": DiseasePathology(
        disease_id="RICE_BROWN_SPOT",
        crop=CropType.RICE,
        common_name="Rice Brown Spot",
        scientific_name="Bipolaris oryzae",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Oval to circular dark brown lesions with yellow halos on rice leaf blades",
            "Spots coalesce causing severe blighting and grain discoloration",
        ],
        immediate_actions=[
            "Correct soil potassium and zinc deficiencies promptly.",
            "Apply protective foliar fungicide at booting or early heading stage.",
        ],
        chemical_medicine_ids=["MED-MCZ-75", "MED-PRO-25"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-PSE-FLU"],
        preventive_measures=[
            "Use certified disease-free seed treated with Pseudomonas fluorescens.",
            "Maintain balanced N-P-K and silicon nutrition in paddy soils.",
        ],
    ),
    "RICE_BACTERIAL_BLIGHT": DiseasePathology(
        disease_id="RICE_BACTERIAL_BLIGHT",
        crop=CropType.RICE,
        common_name="Rice Bacterial Leaf Blight",
        scientific_name="Xanthomonas oryzae pv. oryzae",
        pathogen_type=PathogenType.BACTERIAL,
        key_symptoms=[
            "Water-soaked yellow-orange stripes starting at leaf tips and margins",
            "Wavy necrotic margins drying to straw-white along leaf blades (kresek in seedlings)",
        ],
        immediate_actions=[
            "Drain standing water temporarily and halt nitrogen top-dressing.",
            "Apply recommended bactericide / copper tank mix before panicle initiation.",
        ],
        chemical_medicine_ids=["MED-STR-09", "MED-CPX-50"],
        organic_medicine_ids=["MED-PSE-FLU", "MED-BAC-SUB"],
        preventive_measures=[
            "Grow blight-resistant paddy varieties and avoid clipping seedling tips during transplanting.",
            "Keep irrigation bunds weed-free (remove Leersia hexandra collateral hosts).",
        ],
    ),
    "RICE_TUNGRO": DiseasePathology(
        disease_id="RICE_TUNGRO",
        crop=CropType.RICE,
        common_name="Rice Tungro Virus",
        scientific_name="Rice tungro bacilliform / spherical virus",
        pathogen_type=PathogenType.VIRAL,
        key_symptoms=[
            "Yellow to orange-yellow leaf discoloration starting from leaf tips",
            "Severe plant stunting and reduced tillering transmitted by green leafhoppers",
        ],
        immediate_actions=[
            "Rogue out infected hills early and bury deep in mud to remove viral inoculum.",
            "Target green leafhopper vector populations along field borders using botanical spray.",
        ],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-AZA-10", "MED-PSE-FLU"],
        preventive_measures=[
            "Practice synchronous planting across neighboring paddy plots.",
            "Deploy light traps to monitor Nephotettix virescens vector outbreaks.",
        ],
    ),

    # ADDITIONAL TOMATO PATHOLOGIES
    "TOMATO_LEAF_MOLD": DiseasePathology(
        disease_id="TOMATO_LEAF_MOLD",
        crop=CropType.TOMATO,
        common_name="Leaf Mold",
        scientific_name="Passalora fulva (syn. Fulvia fulva)",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Pale greenish-yellow spots on upper leaf surfaces",
            "Olive-green to velvety purple-brown sporulation on lower leaf undersides",
        ],
        immediate_actions=[
            "Increase greenhouse/canopy ventilation to drop relative humidity below 85%.",
            "Remove heavily affected lower foliage cleanly without shaking spores.",
        ],
        chemical_medicine_ids=["MED-AZX-23", "MED-MCZ-75"],
        organic_medicine_ids=["MED-BAC-SUB", "MED-TRI-VIR"],
        preventive_measures=[
            "Stake and prune suckers to maximize airflow through tomato rows.",
            "Water at the root zone in early morning rather than evening.",
        ],
    ),
    "TOMATO_SEPTORIA_LEAF_SPOT": DiseasePathology(
        disease_id="TOMATO_SEPTORIA_LEAF_SPOT",
        crop=CropType.TOMATO,
        common_name="Septoria Leaf Spot",
        scientific_name="Septoria lycopersici",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Numerous small (2-3mm) circular spots with dark brown borders and gray-white centers",
            "Tiny black pycnidia specks visible in spot centers causing rapid lower defoliation",
        ],
        immediate_actions=[
            "Strip infected bottom leaves and avoid working wet foliage.",
            "Apply broad-spectrum protectant fungicide across middle and upper canopy.",
        ],
        chemical_medicine_ids=["MED-MCZ-75", "MED-CPX-50"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=[
            "Mulch soil surface to eliminate rain-splash spore dispersal.",
            "Sanitize trellises, cages, and stakes between cropping seasons.",
        ],
    ),
    "TOMATO_SPIDER_MITES": DiseasePathology(
        disease_id="TOMATO_SPIDER_MITES",
        crop=CropType.TOMATO,
        common_name="Two-Spotted Spider Mite Infestation",
        scientific_name="Tetranychus urticae",
        pathogen_type=PathogenType.ARTHROPOD,
        key_symptoms=[
            "Fine yellow-white stippling across upper leaf surfaces",
            "Fine silk webbing and bronzing on leaf undersides during hot dry spells",
        ],
        immediate_actions=[
            "Direct pressurized water or miticidal spray to lower leaf undersides.",
            "Avoid broad-spectrum pyrethroids that kill natural predatory mites.",
        ],
        chemical_medicine_ids=["MED-SUL-80"],
        organic_medicine_ids=["MED-AZA-10", "MED-SUL-80"],
        preventive_measures=[
            "Reduce field dust and maintain steady irrigation during heat waves.",
            "Conserve predatory Phytoseiulus mites around field margins.",
        ],
    ),
    "TOMATO_TARGET_SPOT": DiseasePathology(
        disease_id="TOMATO_TARGET_SPOT",
        crop=CropType.TOMATO,
        common_name="Target Spot",
        scientific_name="Corynespora cassiicola",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Small pinpoint water-soaked spots expanding into brown concentric target lesions",
            "Premature yellowing and drop of heavily spotted leaflets",
        ],
        immediate_actions=[
            "Remove severely infected lower leaves and improve canopy aeration.",
            "Apply strobilurin or mancozeb protectant spray on a 7-day interval.",
        ],
        chemical_medicine_ids=["MED-AZX-23", "MED-MCZ-75"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=[
            "Rotate out of solanaceous crops and bury crop residues post-harvest.",
        ],
    ),
    "TOMATO_YELLOW_LEAF_CURL_VIRUS": DiseasePathology(
        disease_id="TOMATO_YELLOW_LEAF_CURL_VIRUS",
        crop=CropType.TOMATO,
        common_name="Tomato Yellow Leaf Curl Virus (TYLCV)",
        scientific_name="Tomato yellow leaf curl Begomovirus",
        pathogen_type=PathogenType.VIRAL,
        key_symptoms=[
            "Upward cupping and curling of young leaflets with interveinal yellowing",
            "Severe plant stunting and flower drop transmitted by silverleaf whiteflies",
        ],
        immediate_actions=[
            "Rogue out early symptomatic plants in sealed bags to protect healthy neighbors.",
            "Control Bemisia tabaci whitefly vectors using neem botanical sprays and yellow sticky traps.",
        ],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-AZA-10", "MED-BIO-NIL"],
        preventive_measures=[
            "Use TYLCV-resistant hybrids and 40-mesh insect-proof nursery nets.",
        ],
    ),
    "TOMATO_MOSAIC_VIRUS": DiseasePathology(
        disease_id="TOMATO_MOSAIC_VIRUS",
        crop=CropType.TOMATO,
        common_name="Tomato Mosaic Virus (ToMV)",
        scientific_name="Tomato mosaic Tobamovirus",
        pathogen_type=PathogenType.VIRAL,
        key_symptoms=[
            "Light and dark green mottled mosaic patterns across leaflets",
            "Fern-leaf narrowing and malformation of young terminal shoots",
        ],
        immediate_actions=[
            "Remove infected plants immediately without brushing against healthy rows.",
            "Wash hands and tools thoroughly in 10% trisodium phosphate or milk solution.",
        ],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-PSE-FLU", "MED-BIO-NIL"],
        preventive_measures=[
            "Use certified virus-free treated seed and avoid tobacco contact prior to handling.",
        ],
    ),

    # ADDITIONAL APPLE, CORN, GRAPE PATHOLOGIES
    "APPLE_BLACK_ROT": DiseasePathology(
        disease_id="APPLE_BLACK_ROT",
        crop=CropType.APPLE,
        common_name="Apple Black Rot (Frogeye Leaf Spot)",
        scientific_name="Botryosphaeria obtusa",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Purple specks enlarging into circular lesions with tan centers and purple borders (frogeye spot)",
            "Mummified black fruit and bark cankers on pruned limbs",
        ],
        immediate_actions=[
            "Prune out dead wood, limb cankers, and mummified fruit from orchard trees.",
            "Apply protectant fungicide from green-tip through petal fall.",
        ],
        chemical_medicine_ids=["MED-MCZ-75", "MED-AZX-23"],
        organic_medicine_ids=["MED-SUL-80", "MED-BAC-SUB"],
        preventive_measures=[
            "Burn or bury pruned infected wood away from orchard rows.",
        ],
    ),
    "APPLE_CEDAR_RUST": DiseasePathology(
        disease_id="APPLE_CEDAR_RUST",
        crop=CropType.APPLE,
        common_name="Cedar Apple Rust",
        scientific_name="Gymnosporangium juniperi-virginianae",
        pathogen_type=PathogenType.FUNGAL_BASIDIOMYCOTA,
        key_symptoms=[
            "Bright yellow-orange leaf spots with tiny dark spermogonia on upper surfaces",
            "Tubular aecia projecting on leaf undersides leading to premature defoliation",
        ],
        immediate_actions=[
            "Apply systemic triazole or protectant fungicide at pink bud through 2nd cover.",
        ],
        chemical_medicine_ids=["MED-HEX-05", "MED-MCZ-75"],
        organic_medicine_ids=["MED-SUL-80", "MED-TRI-VIR"],
        preventive_measures=[
            "Remove nearby eastern red cedar/juniper galls within 300m if feasible.",
        ],
    ),
    "CORN_GRAY_LEAF_SPOT": DiseasePathology(
        disease_id="CORN_GRAY_LEAF_SPOT",
        crop=CropType.CORN,
        common_name="Cercospora Gray Leaf Spot",
        scientific_name="Cercospora zeae-maydis",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Distinctive rectangular matchstick-shaped lesions bounded strictly by leaf veins",
            "Tan to gray necrotic bands coalescing to blight upper ear leaves",
        ],
        immediate_actions=[
            "Apply strobilurin or triazole fungicide at VT-R1 if lesions reach the ear leaf.",
        ],
        chemical_medicine_ids=["MED-AZX-23", "MED-PRO-25"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=[
            "Rotate away from continuous corn and incorporate surface residue.",
        ],
    ),
    "GRAPE_ESCA": DiseasePathology(
        disease_id="GRAPE_ESCA",
        crop=CropType.GRAPE,
        common_name="Esca (Black Measles)",
        scientific_name="Phaeomoniella chlamydospora complex",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Interveinal chlorotic and reddish-brown striping ('tiger-stripe' pattern) on leaves",
            "Dark superficial spotting on ripening grape berries",
        ],
        immediate_actions=[
            "Mark affected vines and prune away dead/cankered spurs during dry weather.",
            "Seal large pruning wounds immediately with Trichoderma-enriched wound paste.",
        ],
        chemical_medicine_ids=["MED-AZX-23", "MED-HEX-05"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=[
            "Avoid pruning during rain; sanitize shears between vines.",
        ],
    ),
    "GRAPE_ISARIOPSIS_SPOT": DiseasePathology(
        disease_id="GRAPE_ISARIOPSIS_SPOT",
        crop=CropType.GRAPE,
        common_name="Isariopsis Leaf Blight",
        scientific_name="Pseudocercospora vitis",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Irregular dark reddish-brown angular blotches across mature vine foliage",
            "Sooty spore tufts on leaf undersides causing late-season defoliation",
        ],
        immediate_actions=[
            "Apply protective copper or mancozeb spray after fruit set.",
        ],
        chemical_medicine_ids=["MED-MCZ-75", "MED-CPX-50"],
        organic_medicine_ids=["MED-SUL-80", "MED-BAC-SUB"],
        preventive_measures=[
            "Ensure open trellis canopy ventilation and collect fallen vineyard leaves.",
        ],
    ),

    # BELL PEPPER PATHOLOGIES
    "BELL_PEPPER_BACTERIAL_SPOT": DiseasePathology(
        disease_id="BELL_PEPPER_BACTERIAL_SPOT",
        crop=CropType.BELL_PEPPER,
        common_name="Bacterial Spot",
        scientific_name="Xanthomonas euvesicatoria",
        pathogen_type=PathogenType.BACTERIAL,
        key_symptoms=[
            "Small water-soaked lesions on lower leaf undersides turning dark brown-black",
            "Heavy leaf yellowing and premature abscission exposing peppers to sunscald",
        ],
        immediate_actions=[
            "Halt overhead irrigation and avoid cultivating wet pepper rows.",
            "Apply copper bactericide + bio-antagonist foliar schedule.",
        ],
        chemical_medicine_ids=["MED-CPX-50", "MED-STR-09"],
        organic_medicine_ids=["MED-PSE-FLU", "MED-BAC-SUB"],
        preventive_measures=[
            "Transplant certified disease-free seedlings and rotate non-solanaceous crops for 3 years.",
        ],
    ),
    "BELL_PEPPER_HEALTHY": DiseasePathology(
        disease_id="BELL_PEPPER_HEALTHY",
        crop=CropType.BELL_PEPPER,
        common_name="Healthy Bell Pepper Canopy",
        scientific_name="Capsicum annuum (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Glossy dark green leaves free of water-soaked spots or mosaic mottling."],
        immediate_actions=["Maintain balanced drip fertigation and weekly pest scouting."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Apply preventive seaweed tonic every 14 days."],
    ),

    # COTTON PATHOLOGIES
    "COTTON_BACTERIAL_BLIGHT": DiseasePathology(
        disease_id="COTTON_BACTERIAL_BLIGHT",
        crop=CropType.COTTON,
        common_name="Cotton Bacterial Blight (Angular Leaf Spot)",
        scientific_name="Xanthomonas citri pv. malvacearum",
        pathogen_type=PathogenType.BACTERIAL,
        key_symptoms=[
            "Angular water-soaked lesions bounded by fine leaf veins turning dark brown-black",
            "Black-arm stem lesions and sunken oily boll spots",
        ],
        immediate_actions=[
            "Apply copper oxychloride + streptocycline foliar spray at early squaring.",
            "Avoid field operations when dew or rain wets the canopy.",
        ],
        chemical_medicine_ids=["MED-CPX-50", "MED-STR-09"],
        organic_medicine_ids=["MED-PSE-FLU", "MED-BAC-SUB"],
        preventive_measures=[
            "Acid-delint and treat cotton seeds before sowing; destroy post-harvest stalks.",
        ],
    ),
    "COTTON_CURL_VIRUS": DiseasePathology(
        disease_id="COTTON_CURL_VIRUS",
        crop=CropType.COTTON,
        common_name="Cotton Leaf Curl Virus (CLCuV)",
        scientific_name="Cotton leaf curl Begomovirus",
        pathogen_type=PathogenType.VIRAL,
        key_symptoms=[
            "Upward or downward leaf cupping with thickened dark green veins",
            "Leafy enations on undersides and stunted bolls transmitted by whiteflies",
        ],
        immediate_actions=[
            "Uproot and destroy early infected plants to curb whitefly acquisition.",
            "Spray neem-based Azadirachtin to suppress Bemisia tabaci whitefly vectors.",
        ],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-AZA-10", "MED-BIO-NIL"],
        preventive_measures=[
            "Plant CLCuV-tolerant cotton hybrids and eradicate weed hosts along field bunds.",
        ],
    ),
    "COTTON_FUSARIUM_WILT": DiseasePathology(
        disease_id="COTTON_FUSARIUM_WILT",
        crop=CropType.COTTON,
        common_name="Cotton Fusarium Wilt",
        scientific_name="Fusarium oxysporum f. sp. vasinfectum",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Yellowing and necrotic browning along leaf margins progressing inward",
            "Vascular brown discoloration inside split main stems and sudden wilting",
        ],
        immediate_actions=[
            "Drench root zone of adjacent healthy plants with Trichoderma viride bio-suspension.",
            "Improve drainage and avoid root-damaging deep inter-row cultivation.",
        ],
        chemical_medicine_ids=["MED-AZX-23", "MED-MCZ-75"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-PSE-FLU"],
        preventive_measures=[
            "Practice 3-year rotation with cereals/sorghum and solarize infested soil.",
        ],
    ),
    "COTTON_HEALTHY": DiseasePathology(
        disease_id="COTTON_HEALTHY",
        crop=CropType.COTTON,
        common_name="Healthy Cotton Crop",
        scientific_name="Gossypium hirsutum (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Broad palmately lobed green foliage without angular lesions or curling."],
        immediate_actions=["Maintain ETL-based bollworm/whitefly pheromone trap monitoring."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Ensure balanced potassium fertilization during boll development."],
    ),

    # HORTICULTURAL & OTHER CROPS (PlantVillage Full 38 Coverage)
    "BLUEBERRY_HEALTHY": DiseasePathology(
        disease_id="BLUEBERRY_HEALTHY",
        crop=CropType.BLUEBERRY,
        common_name="Healthy Blueberry Foliage",
        scientific_name="Vaccinium corymbosum (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Glossy green leaves without scorch or powdery spots."],
        immediate_actions=["Maintain acidic soil pH (4.5-5.2) and drip irrigation."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Apply pine-bark mulch to conserve root moisture."],
    ),
    "CHERRY_POWDERY_MILDEW": DiseasePathology(
        disease_id="CHERRY_POWDERY_MILDEW",
        crop=CropType.CHERRY,
        common_name="Cherry Powdery Mildew",
        scientific_name="Podosphaera clandestina",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=["White powdery fungal mycelium coating young leaves and shoot tips, causing upward curling."],
        immediate_actions=["Prune succulent water sprouts and apply sulphur/triazole spray."],
        chemical_medicine_ids=["MED-HEX-05", "MED-AZX-23"],
        organic_medicine_ids=["MED-SUL-80", "MED-BAC-SUB"],
        preventive_measures=["Open tree canopy for sunlight penetration; avoid excess summer nitrogen."],
    ),
    "CHERRY_HEALTHY": DiseasePathology(
        disease_id="CHERRY_HEALTHY",
        crop=CropType.CHERRY,
        common_name="Healthy Cherry Canopy",
        scientific_name="Prunus cerasus (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Clean serrated green cherry foliage free of powdery mildew."],
        immediate_actions=["Continue routine orchard irrigation and sanitation."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Prune during dormant winter season for optimal airflow."],
    ),
    "ORANGE_CITRUS_GREENING": DiseasePathology(
        disease_id="ORANGE_CITRUS_GREENING",
        crop=CropType.ORANGE,
        common_name="Citrus Greening (Huanglongbing)",
        scientific_name="Candidatus Liberibacter asiaticus",
        pathogen_type=PathogenType.BACTERIAL,
        key_symptoms=[
            "Asymmetrical blotchy yellow mottling across citrus leaf halves",
            "Zinc-deficiency-like interveinal chlorosis and bitter lopsided fruit",
        ],
        immediate_actions=[
            "Control Asian citrus psyllid (Diaphorina citri) vectors immediately using neem oil.",
            "Confirm HLB status via extension lab; remove severely declined inoculum trees.",
        ],
        chemical_medicine_ids=["MED-CPX-50"],
        organic_medicine_ids=["MED-AZA-10", "MED-BIO-NIL"],
        preventive_measures=["Plant only screen-house certified disease-free citrus nursery budwood."],
    ),
    "PEACH_BACTERIAL_SPOT": DiseasePathology(
        disease_id="PEACH_BACTERIAL_SPOT",
        crop=CropType.PEACH,
        common_name="Peach Bacterial Spot",
        scientific_name="Xanthomonas arboricola pv. pruni",
        pathogen_type=PathogenType.BACTERIAL,
        key_symptoms=["Angular purplish-black leaf spots dropping out to form shot-holes and pitted fruit."],
        immediate_actions=["Apply protective copper bactericide at shuck-split and post-rain intervals."],
        chemical_medicine_ids=["MED-CPX-50", "MED-STR-09"],
        organic_medicine_ids=["MED-PSE-FLU", "MED-BAC-SUB"],
        preventive_measures=["Plant windbreaks in sandy orchards to curb wind-driven sand abrasion."],
    ),
    "PEACH_HEALTHY": DiseasePathology(
        disease_id="PEACH_HEALTHY",
        crop=CropType.PEACH,
        common_name="Healthy Peach Foliage",
        scientific_name="Prunus persica (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Elongated green lanceolate peach leaves free of shot-hole lesions."],
        immediate_actions=["Maintain standard orchard fertilization and thinning."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Apply dormant copper at leaf fall as routine sanitation."],
    ),
    "RASPBERRY_HEALTHY": DiseasePathology(
        disease_id="RASPBERRY_HEALTHY",
        crop=CropType.RASPBERRY,
        common_name="Healthy Raspberry Canes",
        scientific_name="Rubus idaeus (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Healthy compound serrated leaves without rust or cane blight."],
        immediate_actions=["Maintain trellis airflow and remove spent floricanes after harvest."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Water at soil line via drip tape."],
    ),
    "SOYBEAN_HEALTHY": DiseasePathology(
        disease_id="SOYBEAN_HEALTHY",
        crop=CropType.SOYBEAN,
        common_name="Healthy Soybean Canopy",
        scientific_name="Glycine max (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Uniform trifoliate green canopy without rust pustules or mosaic."],
        immediate_actions=["Continue standard Rhizobium nodulation and pod-fill moisture monitoring."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Maintain balanced phosphorus and potassium levels."],
    ),
    "SQUASH_POWDERY_MILDEW": DiseasePathology(
        disease_id="SQUASH_POWDERY_MILDEW",
        crop=CropType.SQUASH,
        common_name="Squash Powdery Mildew",
        scientific_name="Podosphaera xanthii",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=["White talcum-like powdery fungal patches on upper and lower cucurbit leaves."],
        immediate_actions=["Apply wettable sulphur or azoxystrobin targeting both leaf surfaces."],
        chemical_medicine_ids=["MED-AZX-23", "MED-HEX-05"],
        organic_medicine_ids=["MED-SUL-80", "MED-BAC-SUB"],
        preventive_measures=["Grow powdery-mildew-tolerant squash hybrids and avoid dense shading."],
    ),
    "STRAWBERRY_LEAF_SCORCH": DiseasePathology(
        disease_id="STRAWBERRY_LEAF_SCORCH",
        crop=CropType.STRAWBERRY,
        common_name="Strawberry Leaf Scorch",
        scientific_name="Diplocarpon earlianum",
        pathogen_type=PathogenType.FUNGAL_ASCOMYCOTA,
        key_symptoms=[
            "Irregular dark purple-red blotches coalescing until leaves look scorched and dry",
        ],
        immediate_actions=["Remove dead scorched runners and apply protectant fungicide."],
        chemical_medicine_ids=["MED-MCZ-75", "MED-AZX-23"],
        organic_medicine_ids=["MED-TRI-VIR", "MED-BAC-SUB"],
        preventive_measures=["Use raised plastic mulch beds and drip irrigation."],
    ),
    "STRAWBERRY_HEALTHY": DiseasePathology(
        disease_id="STRAWBERRY_HEALTHY",
        crop=CropType.STRAWBERRY,
        common_name="Healthy Strawberry Canopy",
        scientific_name="Fragaria × ananassa (Healthy)",
        pathogen_type=PathogenType.PHYSIOLOGICAL,
        key_symptoms=["Lush green trifoliate leaves free of purple scorch blotches."],
        immediate_actions=["Maintain straw/plastic mulch cleanliness and drip watering."],
        chemical_medicine_ids=[],
        organic_medicine_ids=["MED-BIO-NIL"],
        preventive_measures=["Renovate beds after harvest and clear old foliar debris."],
    ),
}

# ---------------------------------------------------------------------------
# 3. Registered Agro-Dealer Stores (Geospatial Network)
# ---------------------------------------------------------------------------

STORE_CATALOG: Dict[str, StoreEntity] = {
    "STR-001": StoreEntity(
        store_id="STR-001",
        store_name="Kisan Agro Kendra & Seed Depot",
        government_license_number="AGR-DL-2023-8841",
        contact_phone="+91-9876543210",
        physical_address="Shop 14, Main Mandi Road, Rural Sector 4, New Delhi",
        latitude=28.6139,
        longitude=77.2090,
        is_verified=True,
        operating_hours="08:00 AM - 08:00 PM (All days)",
    ),
    "STR-002": StoreEntity(
        store_id="STR-002",
        store_name="GreenField Farm Inputs & Bio-Tech Centre",
        government_license_number="AGR-DL-2022-4412",
        contact_phone="+91-9812345678",
        physical_address="Plot 8, Highway 44 Bypass, Model Town, Delhi",
        latitude=28.6420,
        longitude=77.1850,
        is_verified=True,
        operating_hours="08:30 AM - 07:30 PM (Mon-Sat)",
    ),
    "STR-003": StoreEntity(
        store_id="STR-003",
        store_name="Bharat Krishi Vikas Cooperative Store",
        government_license_number="AGR-DL-2021-9923",
        contact_phone="+91-9899001122",
        physical_address="Agricultural Market Yard, Gate 2, Okhla, New Delhi",
        latitude=28.5800,
        longitude=77.2400,
        is_verified=True,
        operating_hours="09:00 AM - 06:00 PM (Mon-Sat)",
    ),
    "STR-004": StoreEntity(
        store_id="STR-004",
        store_name="Jai Kisan Pesticides & Fertilizers",
        government_license_number="AGR-DL-2024-1055",
        contact_phone="+91-9711223344",
        physical_address="Gramin Mandi Chowk, Narela, North Delhi",
        latitude=28.7041,
        longitude=77.1025,
        is_verified=True,
        operating_hours="07:30 AM - 08:30 PM (Mon-Sun)",
    ),
    "STR-005": StoreEntity(
        store_id="STR-005",
        store_name="Annapurna Agri-Service Center",
        government_license_number="AGR-UP-2022-7714",
        contact_phone="+91-9650112233",
        physical_address="Old Bus Stand Road, Sector 15, Noida, UP",
        latitude=28.5355,
        longitude=77.3910,
        is_verified=True,
        operating_hours="08:00 AM - 08:00 PM (Tue-Sun)",
    ),
    "STR-006": StoreEntity(
        store_id="STR-006",
        store_name="National Seeds Corporation Dealer Hub",
        government_license_number="AGR-HR-2023-3390",
        contact_phone="+91-9955443322",
        physical_address="Kisan Bhawan, Old Railway Road, Gurugram, Haryana",
        latitude=28.4595,
        longitude=77.0266,
        is_verified=True,
        operating_hours="09:00 AM - 07:00 PM (Mon-Sat)",
    ),
    "STR-007": StoreEntity(
        store_id="STR-007",
        store_name="Royal Agro-Chemicals & Bio-Solutions",
        government_license_number="AGR-UP-2020-5621",
        contact_phone="+91-9412334455",
        physical_address="Canal Road Crossing, Meerut By-Pass, UP",
        latitude=28.9845,
        longitude=77.7064,
        is_verified=True,
        operating_hours="08:00 AM - 07:00 PM (Mon-Sat)",
    ),
    "STR-008": StoreEntity(
        store_id="STR-008",
        store_name="Progressive Farmers Input Syndicate",
        government_license_number="AGR-HR-2021-8871",
        contact_phone="+91-9466554433",
        physical_address="GT Karnal Road, Near Toll Plaza, Sonipat, Haryana",
        latitude=28.8950,
        longitude=77.0800,
        is_verified=True,
        operating_hours="08:00 AM - 08:00 PM (All days)",
    ),
}

# ---------------------------------------------------------------------------
# 4. Initial Store Inventory Ledgers
# ---------------------------------------------------------------------------

INITIAL_INVENTORY: List[InventoryRecord] = [
    # Store STR-001 (Kisan Agro Kendra, Central Delhi corridor)
    InventoryRecord(store_id="STR-001", medicine_id="MED-MCZ-75", stock_quantity=42, unit_packaging="500g powder pack", unit_price_inr=320.0),
    InventoryRecord(store_id="STR-001", medicine_id="MED-CPX-50", stock_quantity=28, unit_packaging="500g powder pack", unit_price_inr=395.0),
    InventoryRecord(store_id="STR-001", medicine_id="MED-MTX-MZ", stock_quantity=15, unit_packaging="250g powder pack", unit_price_inr=450.0),
    InventoryRecord(store_id="STR-001", medicine_id="MED-TRI-VIR", stock_quantity=60, unit_packaging="1kg bio-pack", unit_price_inr=180.0),
    InventoryRecord(store_id="STR-001", medicine_id="MED-AZA-10", stock_quantity=25, unit_packaging="500ml bottle", unit_price_inr=420.0),
    InventoryRecord(store_id="STR-001", medicine_id="MED-BIO-NIL", stock_quantity=50, unit_packaging="1L tonic bottle", unit_price_inr=290.0),

    # Store STR-002 (GreenField Farm Inputs, West Delhi)
    InventoryRecord(store_id="STR-002", medicine_id="MED-MCZ-75", stock_quantity=18, unit_packaging="500g powder pack", unit_price_inr=310.0),
    InventoryRecord(store_id="STR-002", medicine_id="MED-AZX-23", stock_quantity=12, unit_packaging="200ml bottle", unit_price_inr=780.0),
    InventoryRecord(store_id="STR-002", medicine_id="MED-BAC-SUB", stock_quantity=30, unit_packaging="500ml liquid pack", unit_price_inr=260.0),
    InventoryRecord(store_id="STR-002", medicine_id="MED-TRI-VIR", stock_quantity=35, unit_packaging="1kg bio-pack", unit_price_inr=175.0),

    # Store STR-003 (Bharat Krishi Vikas, Okhla South)
    InventoryRecord(store_id="STR-003", medicine_id="MED-MCZ-75", stock_quantity=8, unit_packaging="500g powder pack", unit_price_inr=325.0),
    InventoryRecord(store_id="STR-003", medicine_id="MED-STR-09", stock_quantity=40, unit_packaging="50g pouch", unit_price_inr=95.0),
    InventoryRecord(store_id="STR-003", medicine_id="MED-PSE-FLU", stock_quantity=22, unit_packaging="1kg bio-pack", unit_price_inr=190.0),
    InventoryRecord(store_id="STR-003", medicine_id="MED-BIO-NIL", stock_quantity=35, unit_packaging="1L tonic bottle", unit_price_inr=280.0),

    # Store STR-004 (Jai Kisan, Narela North)
    InventoryRecord(store_id="STR-004", medicine_id="MED-MCZ-75", stock_quantity=55, unit_packaging="500g powder pack", unit_price_inr=315.0),
    InventoryRecord(store_id="STR-004", medicine_id="MED-MTX-MZ", stock_quantity=32, unit_packaging="250g powder pack", unit_price_inr=440.0),
    InventoryRecord(store_id="STR-004", medicine_id="MED-AZX-23", stock_quantity=19, unit_packaging="200ml bottle", unit_price_inr=770.0),
    InventoryRecord(store_id="STR-004", medicine_id="MED-PRO-25", stock_quantity=24, unit_packaging="250ml bottle", unit_price_inr=490.0),
    InventoryRecord(store_id="STR-004", medicine_id="MED-TRI-VIR", stock_quantity=45, unit_packaging="1kg bio-pack", unit_price_inr=180.0),

    # Store STR-005 (Annapurna Agri-Service, Noida East)
    InventoryRecord(store_id="STR-005", medicine_id="MED-CPX-50", stock_quantity=20, unit_packaging="500g powder pack", unit_price_inr=400.0),
    InventoryRecord(store_id="STR-005", medicine_id="MED-AZA-10", stock_quantity=16, unit_packaging="500ml bottle", unit_price_inr=430.0),
    InventoryRecord(store_id="STR-005", medicine_id="MED-SUL-80", stock_quantity=30, unit_packaging="1kg WDG pack", unit_price_inr=220.0),
    InventoryRecord(store_id="STR-005", medicine_id="MED-BIO-NIL", stock_quantity=25, unit_packaging="1L tonic bottle", unit_price_inr=300.0),

    # Store STR-006 (National Seeds Corp, Gurugram Southwest)
    InventoryRecord(store_id="STR-006", medicine_id="MED-MCZ-75", stock_quantity=22, unit_packaging="500g powder pack", unit_price_inr=318.0),
    InventoryRecord(store_id="STR-006", medicine_id="MED-HEX-05", stock_quantity=14, unit_packaging="500ml bottle", unit_price_inr=360.0),
    InventoryRecord(store_id="STR-006", medicine_id="MED-VAL-03", stock_quantity=18, unit_packaging="1L liquid bottle", unit_price_inr=510.0),
    InventoryRecord(store_id="STR-006", medicine_id="MED-BAC-SUB", stock_quantity=25, unit_packaging="500ml liquid pack", unit_price_inr=265.0),

    # Store STR-007 (Royal Agro, Meerut Outer Corridor ~60km)
    InventoryRecord(store_id="STR-007", medicine_id="MED-MCZ-75", stock_quantity=80, unit_packaging="500g powder pack", unit_price_inr=305.0),
    InventoryRecord(store_id="STR-007", medicine_id="MED-MTX-MZ", stock_quantity=45, unit_packaging="250g powder pack", unit_price_inr=435.0),
    InventoryRecord(store_id="STR-007", medicine_id="MED-PRO-25", stock_quantity=30, unit_packaging="250ml bottle", unit_price_inr=480.0),

    # Store STR-008 (Progressive Farmers, Sonipat ~35km)
    InventoryRecord(store_id="STR-008", medicine_id="MED-MCZ-75", stock_quantity=34, unit_packaging="500g powder pack", unit_price_inr=312.0),
    InventoryRecord(store_id="STR-008", medicine_id="MED-AZX-23", stock_quantity=20, unit_packaging="200ml bottle", unit_price_inr=775.0),
    InventoryRecord(store_id="STR-008", medicine_id="MED-TRI-VIR", stock_quantity=50, unit_packaging="1kg bio-pack", unit_price_inr=170.0),
]
