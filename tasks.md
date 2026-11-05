# tasks.md — DentalGuide SG: Oral-Health Screening Chatbot

## Document Information

- **Feature Name**: DentalGuide SG (working title)
- **Version**: 1.0 (validated by the team, November 5, 2026)
- **Date**: November 5, 2026
- **Author**: [Names of the 2 team members]
- **Related Documents**:
  - Requirements: `requirements.md` (v1.0)
  - Design: `design.md` (v1.0 draft)
  - Working rules and step plan: `CLAUDE.md`

## Implementation Overview

The work follows the 13 steps of `CLAUDE.md`, in order. Each step ends with a stop point and needs explicit approval before the next one starts. The scope is an MVP for 2 people: anything outside `requirements.md` goes to a "future work" list.

### Implementation Strategy

- Close documentation gaps first, so that code is built against consistent requirements.
- Build and evaluate the image model first; the test set is opened only once, at step 5.
- Build the tools and test them without the LLM, then add the agent on top.
- Keep every task traceable to a requirement.

### Development Approach

- **Testing Strategy**: unit tests for critical parts (cost tool, safety rules, image checks); scenario-based Test Log for LLM-dependent behaviour; only results actually obtained are reported.
- **Integration Strategy**: model service, then frontend, then data, tools and agent; end-to-end integration at step 11.
- **Deployment Strategy**: local web application. Phone access for the demo is an open decision (G1).
- **Colab**: training notebooks are generated in the repository and run by the team on Google Colab; the team imports weights, metrics and plots into the repository.
- **Commits**: made manually by the team, one per step. Claude never commits or pushes.
- **Owners**: to be assigned once Person A and Person B are confirmed.

## Open Inputs

| # | Input needed | Blocks |
|---|---|---|
| Q1 | Current module week; real dates for proposal, week 8 review and demo | Scheduling |
| Q2 | LLM constraints, credits and spending limit | Step 10 |
| Q3 | Demo device: team machine, or phone on the local network | G1, task 11.3 |
| Q4 | Person A / Person B, hours per week. Training is confirmed on Colab with a notebook; whether to delete `train_resnet50.py` is still open | Owners, task 1.1 |
| Q5 | Confirmation that the brief in `Downloads` is the right one; copy into `docs/` | Task 1.1 |

## Documentation Gaps to Resolve

Found during step 0. Items marked ✉ need the instructor's answer. No document has been changed yet.

| ID | Gap | Location |
|---|---|---|
| G1 | Local-only design vs. a patient using the app end to end on a phone | design 1, 2.1; NFR Usability; brief 6 |
| G2 ✉ | Brief asks for agentic AI that takes actions; all tools only read local files | brief 5; R5; design 3.5 |
| G3 ✉ | Brief says both "staff could realistically use" and "a patient could use" | brief 5, 6 |
| G4 | R1.4 requires "not a mouth" detection; the design logic does not implement it and states the limit | R1.4; design 3.2; CLAUDE.md |
| G5 | The flow requires an upload before chat, so an emergency message cannot come first | design 3.6; R6.1 |
| G6 | Emergency rules and output filter do not address the multilingual behaviour of R3.6 | R3.6; design 3.4 |
| G7 | Consent text omits the screening result sent to the LLM; provider retention is not covered | design 1, 3.6, 5 |
| G8 | Cost formula undefined: CHAS / Flexi-MediSave order, GST, claims used; `scaling_polishing` key does not match separate CHAS claims | R4.3; design 3.5, 4 |
| G9 | The brief has no restorative subsidy table, needed for the Caries case | brief 1; design 4 |
| G10 | `class_to_care` is incomplete: Hypodontia is empty; Caries spans filling to crown with no display rule | design 4 |
| G11 | No cost behaviour for "uncertain" or no result; no care-setting input | R4.1; brief 2; design 3.5 |
| G12 | R5.1 accepts a postal code, the design limits to a postal district; proximity logic undefined | R5.1; design 5 |
| G13 | `age: int` vs. age band; R8.2 omits citizenship | design 3.5; R8.2; R4.2 |
| G14 | ResNet50 hard-coded in the design although the backbone is chosen after comparison | design 1, 3.2; R2 |
| G15 | No value or calibration method for the confidence threshold; absent from design section 9 | R2.2; design 3.2, 9 |
| G16 | Output filter vs. streaming and the 10-second target; "diagnosis" detection undefined | NFR Performance; design 3.4 |
| G17 | `train_resnet50.py` differs from the design; it evaluates the test set on every run | origin/main; design 3.1; R7.1 |
| G18 | No storage strategy for model weights (file size and GitHub limits to verify) | design 2.1; `.gitignore` |
| G19 | Step 11 of `CLAUDE.md` sets thresholds before the final test, which happens at step 5. Proposed: model thresholds before step 5, agent thresholds at step 11 | CLAUDE.md |
| G20 ✉ | "The brief assumes 4 members" is not stated in the brief; the "no training from scratch" guidance is not written there either | requirements; brief 5 |
| G21 ✉ | Whether `design.md` must follow all sections of `sdd_template` | design 9 |

## Implementation Plan

### Step 0: Framing

- [ ] 0.1 Resolve the documentation gaps
  - Propose a diff for each gap and apply it only after approval
  - _Acceptance: G1 to G21 are each fixed or explicitly deferred in writing; `design.md` section 9 is up to date_
  - _Requirements: R1 to R8_

- [ ] 0.2 Consult the instructor on the ✉ items
  - Ask about G2, G3, G20, G21 and whether `design.md` and `tasks.md` are expected
  - _Acceptance: written answers are archived; affected documents are updated_
  - _Requirements: Brief sections 5 and 6_

### Step 1: Repository skeleton

- [ ] 1.1 Sync the repository and create the structure
  - Pull `origin/main`; add the brief to `docs/`; create the layout from `design.md` section 2.2
  - Keep or retire `train_resnet50.py` according to Q4
  - _Acceptance: local `main` is up to date; the layout exists; G18 is decided_
  - _Requirements: NFR Security_

- [ ] 1.2 Set up the environment
  - Write `requirements.txt` with pinned `torch` and `torchvision`; add `.env.example`
  - _Acceptance: clean install succeeds; `.env` is git-ignored; no secret is tracked_
  - _Requirements: NFR Security_

- [ ] 1.3 Write the initial README and an empty app
  - _Acceptance: following the README, the empty Streamlit app starts_
  - _Requirements: Deliverable "Source code + README"_

### Step 2: Data (Colab, run by the team)

- [ ] 2.1 Download and audit the dataset
  - _Acceptance: 4,375 images and 6 classes are confirmed, or differences are reported; quality, lighting and framing are described_
  - _Requirements: R7.1, R8.5_

- [ ] 2.2 Detect near-duplicates before splitting
  - _Acceptance: perceptual-hash or embedding method documented; duplicate clusters saved; number of clusters reported_
  - _Requirements: R7.1_

- [ ] 2.3 Create the stratified, grouped split
  - _Acceptance: no cluster crosses two sets; class ratios are checked; split and seed are saved to disk_
  - _Requirements: R7.1_

### Step 3: ResNet50 baseline (Colab)

- [ ] 3.1 Train the classification head with the backbone frozen
  - _Acceptance: metrics reported on validation only; training curves saved_
  - _Requirements: R7.3_

- [ ] 3.2 Partially unfreeze the backbone at a lower learning rate
  - _Acceptance: compared with 3.1 on validation macro-F1; no class weights or augmentation, so this stays the baseline_
  - _Requirements: R7.3_

### Step 4: Imbalance and second backbone (Colab)

- [ ] 4.1 Address class imbalance
  - _Acceptance: technique documented; per-class recall and macro-F1 compared with the baseline on validation_
  - _Requirements: R7.3_

- [ ] 4.2 Train a second backbone on the same split
  - _Acceptance: EfficientNet-B0 or similar, trained the same way, with comparable validation metrics_
  - _Requirements: R2 (assumptions)_

- [ ] 4.3 Select the final model
  - _Acceptance: choice justified on validation macro-F1 in `models/model_card.md`; test set still unopened_
  - _Requirements: R2 (assumptions), R7.1_

### Step 5: Final evaluation and export (Colab)

- [ ] 5.1 Fix the model thresholds with the team
  - _Acceptance: minimum macro-F1, minimum recall on pathological classes and confidence threshold are written in `model_card.md` before the test set is opened_
  - _Requirements: R2.2, R7 (assumptions)_

- [ ] 5.2 Run the single final test evaluation
  - _Acceptance: accuracy, per-class precision / recall / F1, macro-F1 and confusion matrix reported; per-class and, where metadata allows, image-quality analysis included_
  - _Requirements: R7.1, R7.2, R8.5_

- [ ] 5.3 Export the model
  - _Acceptance: `.pth` state_dict, `class_names.json`, preprocessing parameters, versions and seed are in `models/`; predictions match between Colab and local on 10 images_
  - _Requirements: R2.1_

### Step 6: Local Model Service

- [ ] 6.1 Implement `image_checks.py`
  - Format, size, brightness and blur checks, plus the mouth check decided in G4
  - _Acceptance: unit tests pass; the model is not called on rejection; a readable message is returned_
  - _Requirements: R1.2, R1.3, R1.4_

- [ ] 6.2 Implement `predict()`
  - _Acceptance: returns top-3 and `ok / uncertain / retake / error`; preprocessing matches the export; exceptions give a readable error; inference time measured against 5 seconds_
  - _Requirements: R2.1, R2.2, R2.5, NFR Performance_

- [ ] 6.3 Add Grad-CAM
  - _Acceptance: an overlay is returned for the selected backbone and checked on sample images_
  - _Requirements: R2.3_

### Step 7: Frontend

- [ ] 7.1 Build the consent screen
  - _Acceptance: upload stays disabled until consent; the notice states what stays local, what goes to the LLM (including the result, G7) and why data is collected_
  - _Requirements: R1.1, R8.2_

- [ ] 7.2 Build the upload flow
  - _Acceptance: a loading indicator shows during analysis; errors and retake requests are displayed_
  - _Requirements: R1.5_

- [ ] 7.3 Build the result panel
  - _Acceptance: top-3, confidence, Grad-CAM, limits note and permanent disclaimer are displayed_
  - _Requirements: R2.1, R2.3, R6.3, R8.3_

### Step 8: Data files

- [ ] 8.1 Build `fees_subsidies.json`
  - _Acceptance: every value has `source_url` and `verified_on`; restorative subsidies are collected (G9); both team members review it_
  - _Requirements: R4.3, R4.4_

- [ ] 8.2 Validate `class_to_care.json`
  - _Acceptance: entries are flagged as team assumptions; empty cases are justified; G10 is closed_
  - _Requirements: R4.6_

- [ ] 8.3 Build the clinic data file
  - _Acceptance: source and date documented; CHAS field included if the source provides it_
  - _Requirements: R5.2_

- [ ] 8.4 Build the product catalogue
  - _Acceptance: no medication; each entry links to a screening class_
  - _Requirements: R5.3_

- [ ] 8.5 Write the knowledge base
  - _Acceptance: sourced HPB / NDCS / MOH notes cover the 6 classes_
  - _Requirements: R3.1, R3.2_

### Step 9: Tools (tested without the LLM)

- [ ] 9.1 Implement `cost_tool`
  - _Acceptance: formula documented (G8); unit tests cover each tier; `missing_fields` works; no-subsidy and no-data cases never invent a figure; calculations are done in code_
  - _Requirements: R4.2, R4.3, R4.5, R4.6_

- [ ] 9.2 Implement `clinic_tool`
  - _Acceptance: area search tested (G12); empty results are handled_
  - _Requirements: R5.1, R5.2, R5.4_

- [ ] 9.3 Implement `product_tool`
  - _Acceptance: suggestions match the class; tests confirm no medication_
  - _Requirements: R5.3_

- [ ] 9.4 Implement `knowledge_tool`
  - _Acceptance: retrieval method chosen by the team; relevant notes returned for sample questions_
  - _Requirements: R3.2_

### Step 10: Agent

- [ ] 10.1 Implement `LLMClient` and the tool-calling loop
  - _Acceptance: provider is swappable; step limit and safe fallback are tested with a fake LLM; keys come from the environment_
  - _Requirements: R3.2, R5.5, NFR Security_

- [ ] 10.2 Implement the input safety guard in `safety.py`
  - _Acceptance: runs before the LLM; gives 995 / A&E first; blocks cost and product tools; language coverage per G6; unit tests pass_
  - _Requirements: R6.1, R6.2_

- [ ] 10.3 Write the system prompt and result explanation
  - _Acceptance: plain language; "possible condition" wording; off-topic redirect; patient's language; dentist advice for uncertain and Normal results; no invented result on failure_
  - _Requirements: R2.2, R2.4, R2.5, R3.1, R3.3, R3.4, R3.5, R3.6, NFR Usability_

- [ ] 10.4 Connect the tools to the agent
  - _Acceptance: the agent asks for missing information; every cost cites its source and is labelled non-binding; failed tools lead to the official CHAS locator_
  - _Requirements: R4.1, R4.2, R4.3, R4.4, R5.1, R5.2, R5.3, R5.4_

- [ ] 10.5 Implement session state
  - _Acceptance: earlier result, tier and area are reused without asking again; state is kept in session memory only_
  - _Requirements: R5.5, R8.1_

- [ ] 10.6 Add the output filter and override resistance
  - _Acceptance: compatible with the streaming decision (G16); diagnosis, medication and override scenarios are refused_
  - _Requirements: R3.4, R3.5, R6.4_

### Step 11: Integration and Test Log

- [ ] 11.1 Integrate the end-to-end flow
  - _Acceptance: consent, upload, result, cost and clinic work in one session; emergency messaging follows G5_
  - _Requirements: R1 to R6_

- [ ] 11.2 Handle external failures
  - _Acceptance: with the LLM or a tool unavailable, a clear message appears, nothing is fabricated and screening still works_
  - _Requirements: R2.5, NFR Reliability_

- [ ] 11.3 Verify performance, phone layout and demo setup
  - _Acceptance: no horizontal scrolling on a phone-sized screen; 5-second and 10-second targets measured on the demo machine; setup follows Q3_
  - _Requirements: NFR Performance, NFR Usability_

- [ ] 11.4 Audit privacy
  - _Acceptance: no image or personal data on disk or in logs without consent; inputs are validated_
  - _Requirements: R8.1, R8.2, NFR Security_

- [ ] 11.5 Write `tests/scenarios.csv` and the agent thresholds
  - _Acceptance: all categories of `design.md` section 7 covered; expected results and pass/fail criteria written before execution and approved_
  - _Requirements: R7.4_

- [ ] 11.6 Run the Test Log
  - _Acceptance: expected, actual and pass/fail recorded; 100% pass on emergency and refusal scenarios; every cost figure matches its source_
  - _Requirements: R7.4, R7.5_

### Step 12: Delivery

- [ ] 12.1 Collect user feedback
  - _Acceptance: questions and pass criteria written beforehand; summary ready for the report_
  - _Requirements: R7.6_

- [ ] 12.2 Finalise the README
  - _Acceptance: a clean install on a fresh machine works by following the README alone_
  - _Requirements: Deliverable "Source code + README"_

- [ ] 12.3 Write the final report
  - _Acceptance: covers problem, design, results, limitations, risks, mitigations, fairness and human oversight; PDPA points verified against official sources_
  - _Requirements: R8.4, R8.5_

- [ ] 12.4 Prepare the presentation and live demo
  - _Acceptance: 15-minute pitch rehearsed and timed; demo run end to end on the demo machine_
  - _Requirements: Deliverable "Presentation"_
