# DentalGuide SG — IT2226 Progress Review 1

Oral-health screening assistant for Singapore patients (IT2226 project, Nanyang Polytechnic).
Team: **Maxime Goulème** and **Maxime Sohier**.

> This tool is a screening and education aid. It does not give a diagnosis and does not recommend medication. All results below are measured on a public dataset only; they are **not** evidence that the system works on real patients.

## Status at Progress Review 1 (19 Nov 2026)

| Part | Status |
|---|---|
| Supervised model (photo of a mouth → 6 classes) | **Done**: data analysis, leak-free split, fine-tuning, comparison of two networks, test evaluation |
| Chatbot (cost and subsidy lookup, clinic search, safety rules) | **Not started**: planned for Progress Review 2 |
| Application skeleton (`app/`) | Empty skeleton only |

## What the model does

A photo of a mouth is classified into one of 6 classes of the Kaggle *Oral Image Dataset*: Calculus, Caries, Hypodontia, Mouth Ulcer, Normal, Tooth Discoloration. We fine-tune networks pre-trained on ImageNet (transfer learning) in two phases: first only the new last layer (baseline), then the whole network.

## Results (all numbers come from the saved outputs of the notebooks)

| | ResNet-50 | EfficientNet-B0 |
|---|---|---|
| Validation macro-F1 (head only → fine-tuned) | 0.757 → 0.910 | 0.785 → 0.933 |
| Best backbone learning rate (3e-5, 1e-4, 3e-4 tested) | 3e-4 | 3e-4 |
| Test macro-F1 / accuracy | 0.904 / 92.7% | 0.907 / 93.5% |
| Test errors (of 399 images) | 29 | 26 |
| Lowest test recall (disease class) | Calculus 0.795 | Calculus 0.818 |
| Parameters / weights file | 23.5 M / 94 MB | 4.0 M / 16 MB |
| CPU time per image (Colab, 1 image) | 117 ms | 34 ms |

- **Success criteria fixed before opening the test set** (ResNet-50): macro-F1 ≥ 0.80 and recall ≥ 0.75 for every disease class. Both are met (0.904; lowest recall 0.795). EfficientNet-B0 also meets both.
- **Model choice.** The rule was fixed by the team on 18 Nov, before training EfficientNet-B0, and applied on **validation only**: EfficientNet-B0 replaces ResNet-50 only if its validation macro-F1 is at least 0.02 higher (≥ 0.9301) and every class has a validation recall ≥ 0.75. Result: 0.9334, so **EfficientNet-B0 is the final model by the rule**. The margin is passed narrowly. On the test set the two models differ by 0.003 macro-F1, which is within noise (one run per model, 399 images): we do not claim that one is more accurate. The rule was fixed after the ResNet-50 test score had already been seen.
- Details: `data/pr1/` (ResNet-50), `data/effnet_b0/` (EfficientNet-B0 and comparison).

## Data and split

- **Source:** [Kaggle Oral Image Dataset](https://www.kaggle.com/datasets/jhirshaikh/oral-image-dataset) (CC0), 4,375 images. **The images are not in this repository**; the notebooks download them with `kagglehub`.
- **Cleaning:** 121 images with contradictory labels, 93 composite images (two photos pasted together, labelled by hand: 77 Calculus, 13 Tooth Discoloration, 3 Mouth Ulcer) and 451 exact duplicates were removed: **3,710 images** remain.
- **Modified copies:** many images are rotated, brighter, zoomed or mirrored versions of the same photo. They are linked with ResNet-50 embeddings (cosine distance ≤ 0.14) into **2,048 groups** (≈ independent photos). Example: Calculus has 732 images but only 180 groups.
- **Split by groups, stratified:** train 2,827 / validation 484 / test 399 images. No group is shared between sets (checked by an assertion). Whole groups move together, so the proportions are 76% / 13% / 11% instead of 70 / 15 / 15.
- The split is stored in `data/eda_v2/data_manifest.csv` (file, class, group, split, MD5) and is shared by all notebooks.

## Reproducing the results

Notebooks run on **Google Colab with a T4 GPU**, in this order, with the same Google account (they exchange files through `MyDrive/dentalguide/`):

1. `notebooks/01_EDA_et_manifest_v2.ipynb` — EDA, cleaning, groups of copies, split, manifest (writes `MyDrive/dentalguide/eda_v2/`).
2. `notebooks/PR1_notebook_ResNet50.ipynb` — ResNet-50: baseline, fine-tuning, learning-rate comparison, test evaluation (writes `MyDrive/dentalguide/pr1/`).
3. `notebooks/02_EfficientNetB0_comparison.ipynb` — EfficientNet-B0 with the same protocol, rule applied on validation, comparison (writes `MyDrive/dentalguide/effnet_b0/`).

Notes:
- The saved outputs come from the runs of 17–18 Nov 2026. The notebooks were translated into English afterwards: code comments and text are in English, but messages and figure titles in the saved outputs are in French. The code logic and the numbers are unchanged.
- Seed 42 everywhere. GPU computation is not bit-for-bit deterministic: re-running notebook 01 may change the manifest slightly, and notebooks 02 and 03 check that the split has the expected sizes (2,827 / 484 / 399).
- **Model weights are not in the repository** (94 MB and 16 MB). They are on Google Drive: `[Drive link to add — shared with the marker]`.
- Run details: `docs/RUN_02_EfficientNetB0.md`.

## Repository structure

```
README.md                 this file
requirements.md, design.md, tasks.md    specification (SDD), design and plan
AI use log Maxime Gouleme.md            AI Use Log
notebooks/                the three notebooks above
data/eda_v2/              manifest, class names, manual composites, EDA figures
data/splits/              split audit tables and figures
data/pr1/                 ResNet-50 results
data/effnet_b0/           EfficientNet-B0 results and comparison
data/knowledge/           knowledge base for the chatbot (Progress Review 2)
docs/                     official brief, run guide
slides/                   Progress Review 1 slides
archive/                  first-protocol scripts, superseded (see below)
app/, models/, tests/     application skeleton (Progress Review 2)
```

`archive/` holds files of the first attempt, kept because the AI Use Log refers to them. They use a random stratified split without groups, which leaks copies between train and test: **do not use them**.

## Limitations

- **Leakage not fully measured.** The split by groups guarantees that no pair closer than 0.14 is shared, but 156 of the 399 test images have a training image closer than 0.18. We have not counted how many are true copies (notebook 01, section 4.2), so we do not claim zero leakage.
- **Possible photo-source bias.** 95.8% of Normal images have a longest side above 1,000 pixels, against 0% in every other class. The perfect Normal score of ResNet-50 may come from the photo source rather than the teeth. Not yet checked (Grad-CAM planned).
- **Small test set** (28 Caries, 44 Calculus), **a single run (seed) per model**, and a learning-rate grid chosen for ResNet-50.
- Caries is over-predicted (ResNet-50: 12 of 35 Caries predictions are wrong); Calculus is often predicted as Caries. Causes are hypotheses, not verified.
- Images are not from Singapore, there is no gum-disease class, and each image has a single label.
- EfficientNet-B0 has a Normal precision of 0.941: some diseased images may be predicted as Normal, which was not the case for ResNet-50. To be checked in its confusion matrix.
- Timings were measured on Colab, not on the target machine.

## Next steps

Grad-CAM; confirm the model choice with several seeds; chatbot with tools (cost estimate with sourced CHAS / MediSave data, clinic search, safety rules, emergencies directed to 995); optimisation and deployment.

## Application skeleton (not functional yet)

Python 3.12. Windows commands shown; on macOS or Linux use `.venv/bin/activate`.

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py      # run
python -m pytest               # test
```

Copy `.env.example` to `.env` and fill in your own key. `.env` is git-ignored: never commit it.

## AI use

AI assistants (Claude) were used throughout. Each use is recorded in `AI use log Maxime Gouleme.md`, with what was accepted, modified or rejected and what was verified.
