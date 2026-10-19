-- Seed Data for Apex Healthcare Supply Intelligence
-- 30 Risk-scored items, 100 Recommended Orders, 15 Substitution Candidates, 3 FDA Recalls, 20 Transfers, Inventory Snapshots

INSERT INTO supply_intel.risk_scores 
(item_id, item_description, item_category, current_on_hand, avg_daily_usage, days_of_supply, risk_score, risk_tier, risk_factors, forecast_demand_30d, forecast_demand_90d)
VALUES
('SKU-PH-101', 'Cefazolin 1g IV Vial (Surgical Prophylaxis)', 'Pharmacy', 42, 28.5, 1.5, 96.4, 'critical', 
 '{"supplier_reliability": 0.28, "lead_time_variance_days": 18, "port_congestion_index": 0.88, "formulary_spike": "OR scheduling +24%"}'::jsonb, 855, 2600),
('SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL', 'Pharmacy', 65, 34.0, 1.9, 94.8, 'critical',
 '{"supplier_reliability": 0.35, "lead_time_variance_days": 21, "port_congestion_index": 0.76, "formulary_spike": "Cardio +18%"}'::jsonb, 1020, 3100),
('SKU-SR-201', '14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor', 'Surgical', 18, 12.0, 1.5, 93.2, 'critical',
 '{"supplier_reliability": 0.40, "lead_time_variance_days": 14, "port_congestion_index": 0.92, "formulary_spike": "ICU census high"}'::jsonb, 360, 1100),
('SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan Emulsion', 'Pharmacy', 55, 30.0, 1.8, 91.5, 'critical',
 '{"supplier_reliability": 0.32, "lead_time_variance_days": 16, "port_congestion_index": 0.81, "formulary_spike": "Surgical volume peak"}'::jsonb, 900, 2750),
('SKU-CC-301', 'Endotracheal Tube 7.5mm Cuffed Murphy Eye', 'Critical Care', 22, 10.5, 2.1, 89.7, 'critical',
 '{"supplier_reliability": 0.45, "lead_time_variance_days": 12, "port_congestion_index": 0.74, "formulary_spike": "Respiratory surge"}'::jsonb, 315, 950),
('SKU-PH-104', 'Epinephrine 1mg/mL (1:1000) 1mL Ampul', 'Pharmacy', 38, 14.0, 2.7, 88.0, 'critical',
 '{"supplier_reliability": 0.41, "lead_time_variance_days": 15, "port_congestion_index": 0.65, "formulary_spike": "Crash cart restock cycle"}'::jsonb, 420, 1260),
('SKU-SR-202', 'Surgical Stapler Endopath 45mm Articulating', 'Surgical', 14, 4.5, 3.1, 86.4, 'critical',
 '{"supplier_reliability": 0.50, "lead_time_variance_days": 10, "port_congestion_index": 0.83, "formulary_spike": "Colorectal cases +30%"}'::jsonb, 135, 410),
('SKU-PH-105', 'Sodium Chloride 0.9% IV Infusion 1000mL Bag', 'Pharmacy', 210, 65.0, 3.2, 85.1, 'critical',
 '{"supplier_reliability": 0.48, "lead_time_variance_days": 11, "port_congestion_index": 0.79, "formulary_spike": "System-wide baseline high"}'::jsonb, 1950, 5900),

('SKU-LB-401', 'High-Sensitivity Troponin I Reagent Kit (100 tests)', 'Laboratory', 8, 2.2, 3.6, 82.3, 'high',
 '{"supplier_reliability": 0.58, "lead_time_variance_days": 9, "port_congestion_index": 0.60, "formulary_spike": "ED chest pain protocol"}'::jsonb, 66, 200),
('SKU-PH-106', 'Nitroglycerin 50mg/250mL in D5W Premix', 'Pharmacy', 15, 3.8, 3.9, 81.0, 'high',
 '{"supplier_reliability": 0.52, "lead_time_variance_days": 8, "port_congestion_index": 0.62, "formulary_spike": "Cath lab demand"}'::jsonb, 114, 350),
('SKU-SR-203', 'Titanium Hemostatic Clips Small 6-clip Cartridge', 'Surgical', 45, 11.0, 4.1, 79.5, 'high',
 '{"supplier_reliability": 0.61, "lead_time_variance_days": 7, "port_congestion_index": 0.58, "formulary_spike": "Vascular cases stable"}'::jsonb, 330, 1000),
('SKU-CC-302', 'Central Venous Catheter Triple Lumen 7 Fr 20cm', 'Critical Care', 28, 6.0, 4.6, 78.2, 'high',
 '{"supplier_reliability": 0.55, "lead_time_variance_days": 8, "port_congestion_index": 0.69, "formulary_spike": "ICU line placement trend"}'::jsonb, 180, 550),
('SKU-PH-107', 'Albuterol Sulfate Inhalation Solution 2.5mg/3mL', 'Pharmacy', 140, 28.0, 5.0, 76.8, 'high',
 '{"supplier_reliability": 0.63, "lead_time_variance_days": 6, "port_congestion_index": 0.51, "formulary_spike": "Seasonal pediatric asthma"}'::jsonb, 840, 2550),
('SKU-GM-501', 'Nitrile Exam Gloves Powder-Free Medium (Box 200)', 'General Medical', 320, 60.0, 5.3, 75.4, 'high',
 '{"supplier_reliability": 0.65, "lead_time_variance_days": 7, "port_congestion_index": 0.68, "formulary_spike": "Inpatient baseline"}'::jsonb, 1800, 5400),
('SKU-SR-204', 'Monocryl 3-0 Suture PS-1 Needle 27 inch Undyed', 'Surgical', 50, 9.0, 5.5, 74.0, 'high',
 '{"supplier_reliability": 0.68, "lead_time_variance_days": 6, "port_congestion_index": 0.54, "formulary_spike": "Plastics and ortho cases"}'::jsonb, 270, 820),
('SKU-PH-108', 'Dextrose 50% Injection 25g/50mL Bristoject Syringe', 'Pharmacy', 30, 5.2, 5.7, 72.5, 'high',
 '{"supplier_reliability": 0.60, "lead_time_variance_days": 7, "port_congestion_index": 0.49, "formulary_spike": "Hypoglycemia protocol"}'::jsonb, 156, 480),
('SKU-LB-402', 'Blood Gas Capillary Tubes Heparinized (Pack 250)', 'Laboratory', 12, 2.0, 6.0, 71.0, 'high',
 '{"supplier_reliability": 0.64, "lead_time_variance_days": 5, "port_congestion_index": 0.52, "formulary_spike": "NICU usage steady"}'::jsonb, 60, 185),

('SKU-CC-303', 'Arterial Line Insertion Kit 20G 12cm Radial', 'Critical Care', 42, 6.5, 6.4, 66.8, 'medium',
 '{"supplier_reliability": 0.70, "lead_time_variance_days": 5, "port_congestion_index": 0.44, "formulary_spike": "Cardiac surgical schedule"}'::jsonb, 195, 600),
('SKU-SR-205', 'Electrosurgical Pencil Rocker Switch w/ Holster', 'Surgical', 85, 12.0, 7.0, 64.2, 'medium',
 '{"supplier_reliability": 0.72, "lead_time_variance_days": 4, "port_congestion_index": 0.41, "formulary_spike": "Main OR rotation"}'::jsonb, 360, 1100),
('SKU-PH-109', 'Vancomycin HCl 1.25g Pharmacy Bulk Package', 'Pharmacy', 70, 9.5, 7.3, 62.5, 'medium',
 '{"supplier_reliability": 0.75, "lead_time_variance_days": 4, "port_congestion_index": 0.38, "formulary_spike": "Antimicrobial stewardship"}'::jsonb, 285, 870),
('SKU-GM-502', 'ChloraPrep One-Step 26mL Applicator Hi-Lite Orange', 'General Medical', 110, 14.5, 7.5, 60.1, 'medium',
 '{"supplier_reliability": 0.77, "lead_time_variance_days": 4, "port_congestion_index": 0.35, "formulary_spike": "Pre-op skin prep standard"}'::jsonb, 435, 1320),
('SKU-LB-403', 'Vacutainer SST Plus Blood Collection Tubes Gold', 'Laboratory', 450, 58.0, 7.7, 58.4, 'medium',
 '{"supplier_reliability": 0.79, "lead_time_variance_days": 3, "port_congestion_index": 0.32, "formulary_spike": "Outpatient draw volume"}'::jsonb, 1740, 5300),
('SKU-PH-110', 'Ondansetron 4mg/2mL Multi-Dose Vial', 'Pharmacy', 130, 16.0, 8.1, 55.7, 'medium',
 '{"supplier_reliability": 0.81, "lead_time_variance_days": 3, "port_congestion_index": 0.30, "formulary_spike": "Post-op PACU standard"}'::jsonb, 480, 1450),
('SKU-CC-304', 'Closed Suction Catheter 14 Fr T-Piece Ventilator', 'Critical Care', 54, 6.2, 8.7, 53.0, 'medium',
 '{"supplier_reliability": 0.82, "lead_time_variance_days": 3, "port_congestion_index": 0.28, "formulary_spike": "VAP prevention bundle"}'::jsonb, 186, 570),
('SKU-SR-206', 'Surgical Skin Stapler 35 Wide Staples', 'Surgical', 90, 10.0, 9.0, 51.2, 'medium',
 '{"supplier_reliability": 0.84, "lead_time_variance_days": 3, "port_congestion_index": 0.26, "formulary_spike": "Wound closure standard"}'::jsonb, 300, 910),

('SKU-GM-503', 'Sterile Gauze Sponges 4x4 12-Ply (Pack 100)', 'General Medical', 420, 35.0, 12.0, 34.5, 'low',
 '{"supplier_reliability": 0.92, "lead_time_variance_days": 2, "port_congestion_index": 0.15, "formulary_spike": "Normal variance"}'::jsonb, 1050, 3200),
('SKU-PH-111', 'Acetaminophen 325mg Oral Tablets (Bottle 1000)', 'Pharmacy', 85, 4.0, 21.2, 22.0, 'low',
 '{"supplier_reliability": 0.95, "lead_time_variance_days": 1, "port_congestion_index": 0.10, "formulary_spike": "Stable floor stock"}'::jsonb, 120, 365),
('SKU-LB-404', 'Urine Specimen Cups Sterile 4oz with Temp Strip', 'Laboratory', 600, 40.0, 15.0, 28.5, 'low',
 '{"supplier_reliability": 0.91, "lead_time_variance_days": 2, "port_congestion_index": 0.12, "formulary_spike": "Standard outpatient usage"}'::jsonb, 1200, 3600),
('SKU-SR-207', 'Suction Tubing Non-Conductive 1/4 inch x 10ft', 'Surgical', 240, 18.0, 13.3, 31.0, 'low',
 '{"supplier_reliability": 0.89, "lead_time_variance_days": 2, "port_congestion_index": 0.18, "formulary_spike": "Standard OR turnover"}'::jsonb, 540, 1650),
('SKU-GM-504', 'Alcohol Prep Pads Sterile Medium (Box 200)', 'General Medical', 800, 50.0, 16.0, 18.4, 'low',
 '{"supplier_reliability": 0.98, "lead_time_variance_days": 1, "port_congestion_index": 0.08, "formulary_spike": "System wide routine"}'::jsonb, 1500, 4500)
ON CONFLICT (item_id) DO UPDATE SET
  current_on_hand = EXCLUDED.current_on_hand,
  days_of_supply = EXCLUDED.days_of_supply,
  risk_score = EXCLUDED.risk_score,
  risk_tier = EXCLUDED.risk_tier,
  risk_factors = EXCLUDED.risk_factors;

-- Seed Substitution Candidates (15 clinical alternatives)
INSERT INTO supply_intel.substitution_candidates
(shortage_item_id, shortage_item_description, alternative_item_id, alternative_item_description, clinical_equivalence, formulary_status, availability, agent_reasoning, confidence_score)
VALUES
('SKU-PH-101', 'Cefazolin 1g IV Vial', 'SKU-PH-ALT-01', 'Ampicillin-Sulbactam 1.5g IV Vial', 'similar', 'on_formulary', 'in_stock',
 'Broad-spectrum beta-lactam coverage suitable for surgical prophylaxis in GI/GYN procedures. Review renal dosing before ordering.', 92.5),
('SKU-PH-101', 'Cefazolin 1g IV Vial', 'SKU-PH-ALT-02', 'Cefuroxime 1.5g IV Vial (Zinacef)', 'equivalent', 'on_formulary', 'available_to_order',
 'Direct 2nd gen cephalosporin alternative with identical coverage for cardiothoracic and orthopedic pre-incisional dosing.', 96.0),
('SKU-PH-101', 'Cefazolin 1g IV Vial', 'SKU-PH-ALT-03', 'Clindamycin 600mg in 50mL D5W IVPB', 'partial', 'on_formulary', 'in_stock',
 'Indicated for severe penicillin/cephalosporin allergic patients. Lacks gram-negative coverage; co-administration with gentamicin recommended.', 87.0),

('SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL', 'SKU-PH-ALT-04', 'Enoxaparin Sodium 40mg/0.4mL Prefilled Syringe', 'similar', 'on_formulary', 'in_stock',
 'LMWH alternative for VTE prophylaxis. Long half-life, requires dose adjustment for CrCl < 30 mL/min.', 94.0),
('SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL', 'SKU-PH-ALT-05', 'Fondaparinux 2.5mg/0.5mL Prefilled Syringe', 'similar', 'restricted', 'in_stock',
 'Synthetic Factor Xa inhibitor for surgical thromboprophylaxis and suspected HIT patients. Restricted pharmacy approval required.', 89.5),
('SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL', 'SKU-PH-ALT-06', 'Bivalirudin 250mg IV Vial', 'partial', 'on_formulary', 'available_to_order',
 'Direct thrombin inhibitor for procedural anticoagulation in cath lab/PCI when heparin-induced thrombocytopenia is suspected.', 85.0),

('SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan Emulsion', 'SKU-PH-ALT-07', 'Etomidate 2mg/mL 10mL Syringe', 'similar', 'on_formulary', 'in_stock',
 'Hemodynamically stable induction agent suitable for rapid sequence intubation. Not indicated for prolonged ICU sedation due to adrenal suppression.', 91.0),
('SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan Emulsion', 'SKU-PH-ALT-08', 'Dexmedetomidine (Precedex) 200mcg/2mL Vial', 'similar', 'on_formulary', 'in_stock',
 'Selective alpha-2 agonist for light-to-moderate ICU sedation without respiratory depression. May cause bradycardia and hypotension.', 88.5),
('SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan Emulsion', 'SKU-PH-ALT-09', 'Midazolam 5mg/mL 2mL Vial', 'partial', 'on_formulary', 'in_stock',
 'Benzodiazepine sedative. Higher risk of delirium in elderly ICU patients compared to propofol; requires flumazenil on hand.', 83.0),

('SKU-SR-201', '14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor', 'SKU-SR-ALT-10', '16 Fr Silicone Elastomer Foley Tray w/ Temp Sensor', 'equivalent', 'on_formulary', 'in_stock',
 'Direct size-adjacent equivalent catheter. Suitable for adult ICU patients without urethral strictures.', 95.0),
('SKU-SR-201', '14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor', 'SKU-SR-ALT-11', '14 Fr Standard 2-Way Foley Tray (Non-Sensor)', 'partial', 'on_formulary', 'in_stock',
 'Identical lumen caliber and comfort; requires secondary axillary or core esophageal temperature probe for hypothermia protocols.', 89.0),

('SKU-CC-301', 'Endotracheal Tube 7.5mm Cuffed Murphy Eye', 'SKU-CC-ALT-12', 'Endotracheal Tube 7.0mm Cuffed Murphy Eye', 'similar', 'on_formulary', 'in_stock',
 'Slightly smaller diameter acceptable for adult female patients or emergency airways where 7.5mm is depleted.', 90.0),
('SKU-CC-301', 'Endotracheal Tube 7.5mm Cuffed Murphy Eye', 'SKU-CC-ALT-13', 'Endotracheal Tube 8.0mm Cuffed Subglottic Suction', 'similar', 'on_formulary', 'in_stock',
 'Premium tube with integrated subglottic drainage lumen, superior for preventing VAP during ventilator stays > 48h.', 93.0),

('SKU-PH-106', 'Nitroglycerin 50mg/250mL in D5W Premix', 'SKU-PH-ALT-14', 'Nitroprusside 50mg/2mL IV Solution (Requires Dilution)', 'similar', 'on_formulary', 'in_stock',
 'Potent arterial and venous vasodilator for acute hypertensive crisis. Requires continuous intra-arterial blood pressure monitoring.', 87.5),
('SKU-PH-106', 'Nitroglycerin 50mg/250mL in D5W Premix', 'SKU-PH-ALT-15', 'Nicardipine 25mg/10mL Ampul IV Infusion', 'similar', 'on_formulary', 'available_to_order',
 'Dihydropyridine calcium channel blocker for blood pressure control without the tachyphylaxis seen with nitroglycerin infusions.', 92.0);

-- Seed Active FDA Recalls (3 active recalls across facilities)
INSERT INTO supply_intel.recall_items
(fda_recall_number, recall_class, item_id, item_description, affected_lot, facility_id, facility_name, location_in_facility, qty_on_hand, patient_exposure_count, recall_date, status)
VALUES
('FDA-2026-REC-0842', 'I', 'SKU-EQ-901', 'Alaris Infusion Pump Model 8015 PCU Door Latch', 'LOT-AL-2025-9921', 'FAC-01', 'Apex Memorial Hospital', 'Central Biomedical Storage - Bay 4', 24, 18, '2026-09-12', 'open'),
('FDA-2026-REC-0842', 'I', 'SKU-EQ-901', 'Alaris Infusion Pump Model 8015 PCU Door Latch', 'LOT-AL-2025-9921', 'FAC-02', 'Apex Children''s Medical Center', 'PICU Clean Utility Rm 3B', 12, 14, '2026-09-12', 'open'),
('FDA-2026-REC-0842', 'I', 'SKU-EQ-901', 'Alaris Infusion Pump Model 8015 PCU Door Latch', 'LOT-AL-2025-9921', 'FAC-03', 'Apex Valley Health', 'Surgical Step-Down Unit', 16, 9, '2026-09-12', 'open'),

('FDA-2026-REC-0719', 'II', 'SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL', 'LOT-HP-88301-B', 'FAC-01', 'Apex Memorial Hospital', 'Main Pharmacy Vault - Pyxis Carousel 2', 40, 31, '2026-09-18', 'open'),
('FDA-2026-REC-0719', 'II', 'SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL', 'LOT-HP-88301-B', 'FAC-04', 'Apex Ambulatory Surgical', 'Pre-Op Medication Refrigerator A', 15, 6, '2026-09-18', 'open'),
('FDA-2026-REC-0719', 'II', 'SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL', 'LOT-HP-88301-B', 'FAC-06', 'Apex Central Distribution Hub', 'Cold Chain Zone 1 - Rack C', 110, 0, '2026-09-18', 'open'),

('FDA-2026-REC-0655', 'III', 'SKU-SR-208', 'Silk Suture 2-0 Braided Black 30 inch (Box 36)', 'LOT-SK-2026-004A', 'FAC-01', 'Apex Memorial Hospital', 'OR Sterile Core - Cabinet 7', 28, 4, '2026-09-21', 'open'),
('FDA-2026-REC-0655', 'III', 'SKU-SR-208', 'Silk Suture 2-0 Braided Black 30 inch (Box 36)', 'LOT-SK-2026-004A', 'FAC-05', 'Apex Northgate Clinic', 'Minor Procedure Supply Closet', 8, 2, '2026-09-21', 'open');

-- Seed Inter-facility Transfer Recommendations (20 records)
INSERT INTO supply_intel.transfer_recommendations
(item_id, item_description, from_facility_id, from_facility_name, to_facility_id, to_facility_name, recommended_qty, reason, from_days_of_supply, to_days_of_supply, status)
VALUES
('SKU-PH-101', 'Cefazolin 1g IV Vial', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-01', 'Apex Memorial Hospital', 150, 'shortage_relief', 24.5, 1.5, 'pending'),
('SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-02', 'Apex Children''s Medical Center', 80, 'shortage_relief', 19.0, 1.9, 'pending'),
('SKU-SR-201', '14 Fr Hydrophilic Foley Catheter Tray', 'FAC-03', 'Apex Valley Health', 'FAC-01', 'Apex Memorial Hospital', 30, 'rebalance', 16.2, 1.5, 'pending'),
('SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-03', 'Apex Valley Health', 90, 'shortage_relief', 22.0, 1.8, 'pending'),
('SKU-CC-301', 'Endotracheal Tube 7.5mm Cuffed', 'FAC-04', 'Apex Ambulatory Surgical', 'FAC-01', 'Apex Memorial Hospital', 25, 'rebalance', 28.0, 2.1, 'pending'),
('SKU-PH-104', 'Epinephrine 1mg/mL Ampul', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-02', 'Apex Children''s Medical Center', 60, 'shortage_relief', 18.5, 2.7, 'pending'),
('SKU-SR-202', 'Surgical Stapler Endopath 45mm', 'FAC-03', 'Apex Valley Health', 'FAC-04', 'Apex Ambulatory Surgical', 12, 'rebalance', 14.0, 3.1, 'pending'),
('SKU-PH-105', 'Sodium Chloride 0.9% IV 1000mL', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-01', 'Apex Memorial Hospital', 400, 'shortage_relief', 21.0, 3.2, 'pending'),
('SKU-LB-401', 'Troponin I Reagent Kit (100 tests)', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-03', 'Apex Valley Health', 10, 'shortage_relief', 15.0, 3.6, 'pending'),
('SKU-PH-106', 'Nitroglycerin 50mg/250mL in D5W', 'FAC-01', 'Apex Memorial Hospital', 'FAC-05', 'Apex Northgate Clinic', 6, 'expiration_prevention', 12.0, 3.9, 'pending'),
('SKU-SR-203', 'Titanium Hemostatic Clips Small', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-01', 'Apex Memorial Hospital', 50, 'rebalance', 25.0, 4.1, 'pending'),
('SKU-CC-302', 'Central Venous Catheter Triple Lumen', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-02', 'Apex Children''s Medical Center', 35, 'shortage_relief', 18.0, 4.6, 'pending'),
('SKU-PH-107', 'Albuterol Sulfate Inhalation 2.5mg', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-02', 'Apex Children''s Medical Center', 120, 'rebalance', 19.5, 5.0, 'pending'),
('SKU-GM-501', 'Nitrile Exam Gloves Medium (Box 200)', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-07', 'Apex Westside Specialty', 80, 'rebalance', 22.0, 5.3, 'pending'),
('SKU-SR-204', 'Monocryl 3-0 Suture PS-1 Needle', 'FAC-04', 'Apex Ambulatory Surgical', 'FAC-01', 'Apex Memorial Hospital', 20, 'rebalance', 16.0, 5.5, 'pending'),
('SKU-PH-108', 'Dextrose 50% Injection 25g/50mL', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-03', 'Apex Valley Health', 25, 'shortage_relief', 20.0, 5.7, 'pending'),
('SKU-LB-402', 'Blood Gas Capillary Tubes Heparinized', 'FAC-01', 'Apex Memorial Hospital', 'FAC-02', 'Apex Children''s Medical Center', 10, 'rebalance', 14.0, 6.0, 'pending'),
('SKU-CC-303', 'Arterial Line Insertion Kit 20G', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-01', 'Apex Memorial Hospital', 40, 'rebalance', 18.5, 6.4, 'pending'),
('SKU-SR-205', 'Electrosurgical Pencil Rocker Switch', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-04', 'Apex Ambulatory Surgical', 30, 'rebalance', 21.0, 7.0, 'pending'),
('SKU-PH-109', 'Vancomycin HCl 1.25g Pharmacy Bulk', 'FAC-06', 'Apex Central Distribution Hub', 'FAC-08', 'Apex Crestview Rehab', 15, 'rebalance', 19.0, 7.3, 'pending');

-- Seed Recommended Orders (100 proposed orders across 8 facilities)
INSERT INTO supply_intel.recommended_orders
(item_id, item_description, supplier_id, supplier_name, recommended_qty, unit_cost, total_cost, order_reason, urgency, confidence_score, model_reasoning, facility_id, facility_name)
SELECT 
  'SKU-' || CASE (i % 6) 
    WHEN 0 THEN 'PH-101' WHEN 1 THEN 'PH-102' WHEN 2 THEN 'SR-201' 
    WHEN 3 THEN 'PH-103' WHEN 4 THEN 'CC-301' ELSE 'PH-105' END,
  CASE (i % 6)
    WHEN 0 THEN 'Cefazolin 1g IV Vial (Surgical Prophylaxis)'
    WHEN 1 THEN 'Heparin Sodium 5,000 USP Units/mL 10mL'
    WHEN 2 THEN '14 Fr Hydrophilic Foley Catheter Tray'
    WHEN 3 THEN 'Propofol 10mg/mL 20mL Diprivan Emulsion'
    WHEN 4 THEN 'Endotracheal Tube 7.5mm Cuffed Murphy Eye'
    ELSE 'Sodium Chloride 0.9% IV Infusion 1000mL Bag' END,
  'SUP-' || LPAD(((i * 7) % 15 + 1)::text, 3, '0'),
  CASE ((i * 7) % 5)
    WHEN 0 THEN 'McKesson Medical-Surgical Inc.'
    WHEN 1 THEN 'Cardinal Health Distribution'
    WHEN 2 THEN 'Medline Industries LP'
    WHEN 3 THEN 'AmerisourceBergen Healthcare'
    ELSE 'Baxter Healthcare Supply' END,
  ((i * 13) % 40 + 10) * 10,
  ROUND((((i * 19) % 80 + 15)::numeric), 2),
  ROUND((((i * 13) % 40 + 10) * 10 * (((i * 19) % 80 + 15)::numeric)), 2),
  CASE (i % 4)
    WHEN 0 THEN 'shortage_prevention'
    WHEN 1 THEN 'restock'
    WHEN 2 THEN 'safety_stock'
    ELSE 'recall_replacement' END,
  CASE (i % 3)
    WHEN 0 THEN 'emergency'
    WHEN 1 THEN 'expedite'
    ELSE 'routine' END,
  ROUND((82.0 + (i % 17)::numeric), 1),
  'ML Model v4.2 detected stock velocity surge: days of supply dropping below safety threshold before next normal procurement cycle.',
  'FAC-0' || ((i % 8) + 1),
  CASE (i % 8)
    WHEN 0 THEN 'Apex Memorial Hospital'
    WHEN 1 THEN 'Apex Children''s Medical Center'
    WHEN 2 THEN 'Apex Valley Health'
    WHEN 3 THEN 'Apex Ambulatory Surgical'
    WHEN 4 THEN 'Apex Northgate Clinic'
    WHEN 5 THEN 'Apex Central Distribution Hub'
    WHEN 6 THEN 'Apex Westside Specialty'
    ELSE 'Apex Crestview Rehab' END
FROM generate_series(1, 100) AS i;

-- Seed Inventory Snapshots
INSERT INTO supply_intel.inventory_snapshot
(item_id, item_description, facility_id, facility_name, location, on_hand_qty, lot_number, expiration_date, unit_cost)
VALUES
('SKU-PH-101', 'Cefazolin 1g IV Vial', 'FAC-01', 'Apex Memorial Hospital', 'Pharmacy Vault - Pyxis Carousel 1', 28, 'LOT-CF-2025-110', '2026-12-31', 14.50),
('SKU-PH-101', 'Cefazolin 1g IV Vial', 'FAC-01', 'Apex Memorial Hospital', 'Main OR Satellite Core 2', 14, 'LOT-CF-2025-112', '2027-02-28', 14.50),
('SKU-PH-101', 'Cefazolin 1g IV Vial', 'FAC-06', 'Apex Central Distribution Hub', 'Zone B - Pharmaceutical Cold Cage', 150, 'LOT-CF-2026-004', '2027-08-31', 13.80),
('SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL', 'FAC-01', 'Apex Memorial Hospital', 'Main Pharmacy Vault - Pyxis Carousel 2', 40, 'LOT-HP-88301-B', '2026-11-15', 22.10),
('SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL', 'FAC-02', 'Apex Children''s Medical Center', 'PICU Clean Utility Rm 3B', 25, 'LOT-HP-88305-A', '2027-01-31', 22.10),
('SKU-SR-201', '14 Fr Hydrophilic Foley Catheter Tray', 'FAC-01', 'Apex Memorial Hospital', 'Urology Sterile Supply - Aisle 3', 18, 'LOT-FL-9931', '2027-06-30', 48.00),
('SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan', 'FAC-01', 'Apex Memorial Hospital', 'Anesthesia Workroom 1 - Safe B', 35, 'LOT-PR-7714', '2026-10-31', 32.50),
('SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan', 'FAC-03', 'Apex Valley Health', 'Surgical Step-Down Unit Refrigerator', 20, 'LOT-PR-7719', '2026-11-30', 32.50),
('SKU-CC-301', 'Endotracheal Tube 7.5mm Cuffed', 'FAC-01', 'Apex Memorial Hospital', 'Respiratory Therapy Bay 1', 22, 'LOT-ET-5510', '2028-04-30', 16.75),
('SKU-PH-104', 'Epinephrine 1mg/mL Ampul', 'FAC-01', 'Apex Memorial Hospital', 'Emergency Code Carts (Units 1-8)', 38, 'LOT-EP-3341', '2026-12-15', 18.20),
('SKU-SR-202', 'Surgical Stapler Endopath 45mm', 'FAC-01', 'Apex Memorial Hospital', 'Minimally Invasive OR Pack Room', 14, 'LOT-ST-6620', '2027-09-30', 215.00),
('SKU-PH-105', 'Sodium Chloride 0.9% IV 1000mL', 'FAC-01', 'Apex Memorial Hospital', 'IV Fluid Staging Central', 210, 'LOT-SC-1190', '2027-05-31', 4.10)
ON CONFLICT (item_id, facility_id, lot_number) DO NOTHING;
