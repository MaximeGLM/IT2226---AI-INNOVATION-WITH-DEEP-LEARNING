# requirements.md — DentalGuide SG: Oral-Health Screening Chatbot for Singapore Patients

## Document Information

- **Feature Name**: DentalGuide SG (working title)
- **Version**: 1.0
- **Date**: November 5, 2026
- **Author**: [Names of the 2 team members]
- **Stakeholders**: Singapore patients (end users), Course instructor (IT2226), Dental clinics (indirect beneficiaries)
- **Course / Brief**: IT2226 AI Innovator and Deep Learning Project — _Dental Health Awareness and Affordability in Singapore_

## Introduction

Dental disease in Singapore is common, mostly painless in its early stages, and expensive once treated. Patients often cannot recognise early problems, cannot interpret a screening result, do not know what they would pay after CHAS / MediSave subsidies, and must run many separate searches to find a clinic. The brief defines four gaps: **detection, understanding, cost, and action**.

Our team (2 members instead of the usual 4) will build a chatbot-based prototype that closes these four gaps. A patient uploads a photo of their mouth; a **fine-tuned pre-trained image model** screens it for six common conditions; a **chatbot powered by an existing LLM** explains the result in plain language, answers the patient's follow-up questions, estimates the out-of-pocket cost, and uses **tools (agentic AI)** to find a suitable clinic and home-care products.

The system is a **screening and education aid only**. It never gives a diagnosis and never recommends medication. Following the instructor's guidance, **no model is trained from scratch**: both the vision model (transfer learning / fine-tuning) and the language model (used as-is through its API, with prompts and tools) start from existing models.

### Feature Summary

A Singapore-specific chatbot that screens an oral photo with a fine-tuned image classifier, explains the pre-screening result in plain language, estimates the post-subsidy cost with cited sources, and helps the patient find a clinic and home-care products.

### Business Value

- Earlier detection of dental problems, when treatment is cheapest (e.g. a cleaning costs far less than a molar root canal).
- Clearer understanding of results and of subsidies (CHAS, MediSave, Flexi-MediSave), reducing delay caused by fear of cost.
- A single entry point replacing several separate searches (clinic, price, subsidy, products).

### Scope

**In scope**

- Image upload and 6-class screening (Calculus, Hypodontia, Tooth Discoloration, Normal, Mouth Ulcer, Caries) using the Kaggle Oral Image Dataset.
- Chatbot that explains the screening result and answers patient questions about it (what it is, causes, progression, urgency, what a visit involves).
- Cost estimation (Singapore fees + CHAS / MediSave rules) with cited sources and a non-binding disclaimer.
- Agent tools: clinic search, home-care product search.
- Emergency detection and redirection to 995 / A&E.
- Evaluation of both the model and the agent; responsible-AI measures (fairness, privacy/PDPA, transparency, risk of error).

**Out of scope**

- Any diagnosis, prescription, or medication advice.
- Training a model from scratch.
- Gum-disease detection (not a labelled class in the dataset — documented as a limitation).
- User accounts, booking appointments, payments, or storing patient history.
- Real-time clinic availability or real-time prices.
- Native mobile app (web interface only).

## Requirements

### Requirement 1: Oral Photo Upload and Consent

**User Story:** As a patient, I want to upload a photo of my mouth after understanding how it will be used, so that I can get a screening result without worrying about my personal data.

#### Acceptance Criteria

1. WHEN the patient opens the application THEN the Frontend SHALL display a notice explaining that the tool is a screening aid (not a diagnosis) and how the image is handled, and SHALL require explicit consent before upload is enabled.
2. WHEN the patient uploads an image THEN the Backend SHALL validate its format (JPEG/PNG) and size before processing.
3. IF the file is not a valid image or exceeds the size limit THEN the Backend SHALL reject it with a clear error message and SHALL NOT call the model.
4. IF the image is too dark, too blurry, or does not appear to show a mouth THEN the Backend SHALL ask the patient to retake the photo instead of returning a screening result.
5. WHILE the image is being analysed THEN the Frontend SHALL display a loading indicator.

#### Additional Details

- **Priority**: High
- **Complexity**: Medium
- **Dependencies**: None
- **Assumptions**: Quality / "is this a mouth" check can be done with a simple heuristic or a confidence threshold; its limits are documented.

### Requirement 2: Oral Condition Screening Model (Detection Gap)

**User Story:** As a patient, I want the system to tell me which common oral condition my photo most resembles, so that I can notice problems before they become painful.

#### Acceptance Criteria

1. WHEN a valid image is submitted THEN the Model Service SHALL return the top-3 predicted classes with confidence scores among the 6 dataset classes.
2. WHEN the top prediction confidence is below a defined threshold THEN the Model Service SHALL flag the result as "uncertain" and the Chatbot SHALL recommend seeing a dentist rather than presenting a confident result.
3. WHEN a result is returned THEN the Model Service SHALL also return a visual explanation (e.g. Grad-CAM heatmap) of the image regions that influenced the prediction.
4. WHERE the predicted class is "Normal" THEN the Chatbot SHALL still state that a screening cannot replace a routine dental check-up.
5. IF the model service fails THEN the Backend SHALL return a readable error and the Chatbot SHALL NOT invent a result.

#### Additional Details

- **Priority**: High
- **Complexity**: High
- **Dependencies**: Requirement 1
- **Assumptions**: A pre-trained image classifier (e.g. EfficientNet / ResNet / MobileNet family, pre-trained on ImageNet) is fine-tuned on the Kaggle dataset; the final backbone is chosen by comparing at least two candidates on the validation set.

### Requirement 3: Plain-Language Explanation and Q&A (Understanding Gap)

**User Story:** As a patient, I want the chatbot to explain my screening result and answer my questions in simple words, so that I understand what it means and how urgent it is.

#### Acceptance Criteria

1. WHEN a screening result is available THEN the Chatbot SHALL explain, in plain language, what the condition is, common causes, how it can progress, and how urgent it is.
2. WHEN the patient asks a follow-up question about the result THEN the Chatbot SHALL answer using the screening result as context and a curated knowledge base (HPB / NDCS / MOH material).
3. WHEN the patient asks something outside oral health THEN the Chatbot SHALL politely redirect to its purpose.
4. WHEN presenting any result THEN the Chatbot SHALL describe it as a "screening result / possible condition" and SHALL NOT state it as a diagnosis.
5. IF the patient asks for medication, dosage, or a diagnosis THEN the Chatbot SHALL decline and recommend consulting a licensed dentist.
6. WHERE the patient writes in a language supported by the LLM THEN the Chatbot SHALL answer in that language.

#### Additional Details

- **Priority**: High
- **Complexity**: Medium
- **Dependencies**: Requirement 2
- **Assumptions**: An existing LLM is used through its API with a system prompt and retrieved reference content; no LLM fine-tuning.

### Requirement 4: Evaluation of the Model and the Agent

**User Story:** As the project team (and the assessors), I want evidence that both the model and the agent work and are safe, so that the results can be trusted.

#### Acceptance Criteria

1. WHEN the dataset is prepared THEN the team SHALL split it into train / validation / test sets with stratification, and SHALL keep the test set untouched until the final evaluation.
2. WHEN the model is evaluated THEN the team SHALL report accuracy, per-class precision / recall / F1, macro-F1, and a confusion matrix on the test set.
3. WHEN class imbalance is addressed (smallest class Caries ≈ 219 images vs. Calculus ≈ 1,296) THEN the team SHALL document the technique used (class weights, augmentation, or resampling) and compare with a baseline.
4. WHEN the agent is evaluated THEN the team SHALL run a written test log of scenarios covering: correct tool selection, correct cost figures against the cited source, emergency redirection, refusal of diagnosis/medication, out-of-scope questions, and missing-information handling.
5. WHEN testing is complete THEN the team SHALL record each scenario's expected result, actual result, and pass/fail in the Test Log.
6. WHEN possible THEN the team SHALL collect feedback from at least a few real users and summarise it in the report.

#### Additional Details

- **Priority**: High
- **Complexity**: Medium
- **Dependencies**: Requirements 2 to 6
- **Assumptions**: Pass/fail criteria (e.g. minimum macro-F1, 100% pass on emergency and refusal scenarios) are fixed _before_ testing, as taught in the Design Thinking session.

### Requirement 5: Responsible AI and PDPA

**User Story:** As a patient, I want my data protected and the limits of the system to be clear, so that I can trust it.

#### Acceptance Criteria

1. WHEN an image or conversation is processed THEN the Backend SHALL NOT store it beyond the session unless the patient explicitly consents.
2. WHEN the application is used THEN the system SHALL collect only the data needed (area, subsidy tier, age band) and SHALL tell the patient why.
3. WHEN a screening result is shown THEN the system SHALL display the model's confidence and a short note on its limits (non-Singapore images, no gum-disease class, single label per image).
4. WHEN the final report is written THEN the team SHALL document risks (false negatives, false positives, bias, LLM hallucination, outdated fees), their mitigations, and the human-oversight position (a dentist makes any diagnosis).
5. WHEN fairness is assessed THEN the team SHALL analyse per-class performance and, where metadata allows, performance across image quality and lighting conditions, and report that the dataset is not Singaporean.

#### Additional Details

- **Priority**: Medium
- **Complexity**: Medium
- **Dependencies**: Requirements 1, 2, 3
- **Assumptions**: Principles from the Responsible AI course (fairness, transparency, robustness, accountability, privacy) and Singapore's Model AI Governance Framework are used as the checklist.

## Non-Functional Requirements

### Performance Requirements

- WHEN a valid image is submitted THEN the Model Service SHALL return a prediction within 5 seconds on the team's demo machine.
- WHEN the patient sends a chat message THEN the Chatbot SHALL start answering within 10 seconds under normal conditions.

### Security Requirements

- WHEN the Backend receives any input THEN it SHALL validate and sanitise it before processing.
- WHEN API keys are used THEN they SHALL be stored in environment variables and SHALL NOT be committed to the repository.

### Usability Requirements

- WHEN the application is viewed on a phone-sized screen THEN the Frontend SHALL remain usable without horizontal scrolling.
- WHEN the Chatbot answers THEN it SHALL use plain language suitable for a non-expert adult.

### Reliability Requirements

- IF an external service (LLM API, clinic data source) is unavailable THEN the system SHALL show a clear error message and SHALL NOT fabricate an answer.

## Constraints and Assumptions

### Technical Constraints

- The image model must be a **pre-trained model fine-tuned on the dataset** (no training from scratch); the model notebook with the saved model is a deliverable.
- The language model is an **existing LLM used through an API** (no training); agentic behaviour is implemented with tool/function calling.
- Core dataset: Kaggle Oral Image Dataset (jhirshaikh), 4,375 images, 6 classes, CC0.
- Programming language: Python; training done in a notebook (e.g. Google Colab with free GPU).

### Business Constraints

- **Team of 2** (the brief assumes 4): scope is deliberately kept to a minimum viable prototype that closes the four gaps; extra features are listed as "future work".
- Timeline follows the module schedule: proposal (weeks 1–2), model (3–8, mid-term review in week 8), agent (9–12), integration and testing (13–14), final presentation and demo (15–16).
- Singapore context only: fees and subsidies are Singapore's.

### Assumptions

- The images are not from Singapore patients, so real-world performance may be lower than test-set performance.
- Fee and subsidy data change over time; every figure carries its source and verification date.
- Users are adults who can take a reasonably clear photo of their mouth with a phone.

## Planned Deliverables (from the brief)

| Deliverable          | Planned content                                                        | Requirements |
| -------------------- | ---------------------------------------------------------------------- | ------------ |
| Project proposal     | This document + design.md + tasks.md                                   | All          |
| Model notebook       | Fine-tuning and evaluation of the pre-trained image model, saved model | 2, 7         |
| Source code + README | Backend, chatbot, tools, frontend, run instructions                    | 1–6          |
| Working prototype    | Web app usable end to end by a patient                                 | 1–6          |
| Test log             | Scenarios, expected vs. actual results                                 | 7            |
| Final report         | Problem, design, results, limitations, responsible AI                  | 7, 8         |
| Presentation         | 15-minute pitch + live demo                                            | All          |

## Proposed Work Split (2 people)

| Area                                                       | Person A | Person B |
| ---------------------------------------------------------- | -------- | -------- |
| Image model (data prep, fine-tuning, evaluation, Grad-CAM) | Lead     | Review   |
| Agent (LLM, tools, prompts, safety rules)                  | Review   | Lead     |
| Cost and clinic data files (MOH / CHAS / CPF)              | Support  | Lead     |
| Frontend + integration                                     | Lead     | Support  |
| Test log, report, presentation                             | Shared   | Shared   |

## Success Criteria

### Definition of Done

- [ ] All acceptance criteria in Requirements 1–8 are met
- [ ] Non-functional requirements are satisfied
- [ ] Model notebook, source code + README, prototype, test log, report and presentation are delivered
- [ ] All safety scenarios in the Test Log pass

### Acceptance Metrics

- Test-set macro-F1 reported, with per-class results and confusion matrix (target value fixed before the final test).
- 100% of emergency and "refuse diagnosis/medication" test scenarios passed.
- 100% of cost figures shown match the cited source in the data file.
- Every cost figure displayed carries a source and a non-binding disclaimer.

## Glossary

| Term                            | Definition                                                                                                            |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Screening                       | A quick check that suggests a possible condition; not a diagnosis                                                     |
| Fine-tuning / transfer learning | Re-training the last layers (or all layers) of an existing pre-trained model on our own data                          |
| Agentic AI                      | An AI that decides which tools to call (cost estimate, clinic search, product search) to complete a task for the user |
| LLM                             | Large Language Model, the existing language model that powers the chatbot                                             |
| Grad-CAM                        | A technique that highlights the image regions that most influenced a prediction                                       |
| CHAS                            | Community Health Assist Scheme, Singapore government subsidy card with tiers (Pioneer, Merdeka, Blue, Orange, Green)  |
| MediSave / Flexi-MediSave       | CPF savings usable for certain medical (and some dental) expenses                                                     |
| PDPA                            | Singapore's Personal Data Protection Act                                                                              |
| Macro-F1                        | F1-score averaged equally over all classes; suited to imbalanced datasets                                             |

## Risks

| Risk                                       | Impact                           | Mitigation                                                    |
| ------------------------------------------ | -------------------------------- | ------------------------------------------------------------- |
| Only 2 team members                        | Not enough time for all features | Strict MVP; one tool at a time; future-work list              |
| Imbalanced dataset                         | Poor recall on Caries / Ulcer    | Class weights, augmentation, per-class metrics                |
| Non-Singapore images, no gum-disease class | Real-world errors                | Display confidence and limits; always recommend a dentist     |
| LLM hallucination (fees, subsidies)        | Wrong cost information           | Costs come only from the data file via the tool; cite sources |
| Outdated fees / subsidies                  | Wrong estimates                  | Version data with "verified on" date; disclaimer              |

---

## Requirements Review Checklist

### Completeness

- [x] All user stories have clear roles, features, and benefits
- [x] Each requirement has acceptance criteria using EARS format
- [x] Non-functional requirements are addressed
- [x] Success criteria are defined and measurable

### Traceability

- [x] Requirements are numbered and organized
- [x] Dependencies between requirements are stated
- [x] Requirements link to the four gaps of the brief (Detection → R2, Understanding → R3, Cost → R4, Action → R5)
- [x] Assumptions and constraints are documented
