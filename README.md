# DentalGuide SG

Oral-health screening chatbot for Singapore patients (IT2226 project). This tool is a screening and education aid: it does not give a diagnosis and does not recommend medication.

**Status**: step 1, empty skeleton. See `tasks.md` for the plan.

## Requirements

- Python 3.12
- Windows commands are shown below; on macOS or Linux, use `.venv/bin/activate`

## Setup

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own key. `.env` is git-ignored: never commit it.

## Run

```bash
streamlit run app/main.py
```

## Test

```bash
python -m pytest
```

## Project documents

- `requirements.md`: what the system must do
- `design.md`: how it is designed
- `tasks.md`: implementation plan
- `docs/`: official brief
