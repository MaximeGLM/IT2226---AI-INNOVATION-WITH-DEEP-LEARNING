# How to run `02_EfficientNetB0_comparison.ipynb`

Guide for Maxime. Notebook: [`notebooks/02_EfficientNetB0_comparison.ipynb`](../notebooks/02_EfficientNetB0_comparison.ipynb).

## 1. What the notebook does

It trains **EfficientNet-B0** with exactly the same protocol as the ResNet-50 in `PR1_notebook_ResNet50.ipynb`. That means the same manifest, the same split (2,827 / 484 / 399), the same augmentation, the same class weights, the same two phases (3 + 8 epochs) and the same learning-rate grid. Then it compares the two models. This covers R2 ("choose the final backbone by comparing at least two candidates on the validation set") and task 4.2 in `tasks.md`.

**Comparison rule, fixed by the team on 18 Nov 2026 before any EfficientNet training (option B):**

> EfficientNet-B0 replaces ResNet-50 as the final model **only if** its validation macro-F1 is at least **ResNet-50's validation macro-F1 + 0.02** (0.9101 + 0.02 = 0.9301) **and** every class has a validation recall ≥ 0.75. Otherwise ResNet-50 stays the final model. Both models are then evaluated **once** on the test set, for the report only; the test result **never** changes the choice.

The notebook enforces this order:
1. It saves the rule to Drive.
2. It decides on the validation set.
3. It saves `decision.json`.
4. Only then does it open the test set.

**Do not edit the rule cell (section 2).**

## 2. Before you start: files needed on your Google Drive

The notebook reads two folders from **your own** Drive. The paths must be exactly these:

| Folder | Files | Created by |
|---|---|---|
| `MyDrive/dentalguide/eda_v2/` | `data_manifest.csv`, `class_names.json` | `01_EDA_et_manifest_v2.ipynb` |
| `MyDrive/dentalguide/pr1/` | `run_info.json`, `resnet50_dental.pt` (≈ 94 MB), `training_history.csv` | `PR1_notebook_ResNet50.ipynb` |

**Important: use the team's PR1 files, do not retrain ResNet-50.** The rule compares against the ResNet-50 of PR1 (validation macro-F1 **0.9101**, test macro-F1 0.904). If you re-run the PR1 notebook, you get a new ResNet-50 with slightly different numbers. It also opens the test set again. The comparison would then no longer match what the team presented at PR1.

Ask for the two folders and copy them to your Drive under the same paths. The simplest way:
1. Download the folders from the other Drive.
2. Upload them into `MyDrive/dentalguide/` on yours.

A Drive *shortcut* to a shared folder may also work, but I have not checked this. Copying the files is the safe option.

**Check:** in section 2, the notebook prints the threshold. It must say **0.9301**. If it shows another value, your `pr1/run_info.json` is not the team's file.

## 3. Open the notebook in Colab

The repository is private, so Colab needs access to GitHub:
1. Go to <https://colab.research.google.com>, then **File > Open notebook > GitHub**.
2. Tick **Include private repos** and authorise GitHub if asked.
3. Choose `MaximeGLM/IT2226---AI-INNOVATION-WITH-DEEP-LEARNING`, branch `main`, then `notebooks/02_EfficientNetB0_comparison.ipynb`.

Alternative: download the `.ipynb` from GitHub and use **File > Upload notebook**.

## 4. Run it

1. **Runtime > Change runtime type > T4 GPU.**
2. **Runtime > Run all**, or run the cells in order. Accept the Google Drive access when asked.
3. Dataset download (`kagglehub`): if it asks for authentication, create a Kaggle API token (**Kaggle > Settings > API > Create New Token**). Then add `KAGGLE_USERNAME` and `KAGGLE_KEY` in the Colab **Secrets** (🔑 icon). Never paste the key into a cell.
4. Before the grid starts, a quick 1-epoch test (section 5.1) checks that everything runs.

**Run time:** the notebook prints the duration of the learning-rate grid (3 trainings). For the expected time, ask for the figure from the first run.

## 5. What you should see

| Section | Expected output |
|---|---|
| 2 | `Règle enregistrée : … macro-F1 val >= 0.9301 …` |
| 3 | `Même manifest et même découpage que le PR1 : {'train': 2827, 'val': 484, 'test': 399}` |
| 5 | Number of parameters of both models, then the training logs of 3 runs |
| 6 | Validation reports of both models, then `==> MODÈLE FINAL (décidé sur la validation) : …` |
| 7 | Test reports of both models. **ResNet-50 must give back the PR1 test results** (macro-F1 0.904, 29 errors out of 399). This is the reproducibility check. |
| 8 | Comparison table: size, speed, validation and test metrics |

The two ✍️ cells (training interpretation, comparative assessment) must be written **by you, in your own words**.

## 6. Two runs, one official result

The notebook has already been run once by your teammate. Results can differ slightly between two runs (GPU, mixed precision, non-deterministic operations), even with the same seed.

- **Agree before you compare the two runs** on which run is the official one. The simplest choice is the first run.
- **Never pick the run with the better test score.** That would be selection on the test set, exactly what the rule is meant to avoid.
- If the two runs reach different decisions in section 6, that is a sign that the gap between the models is within the noise. Write it in the report. Do not hide it.

**Drive:** each person writes to their own `MyDrive/dentalguide/effnet_b0/`. If you share that folder, the notebook stops when it finds a different rule and overwrites `decision.json`. So keep your own folder.

## 7. After the run

1. Files saved in `MyDrive/dentalguide/effnet_b0/`:
   - `comparison_rule.json`, `decision.json`, `comparison.csv`, `run_info.json`
   - `hyperparameter_results.csv`, `training_history.csv`, `classification_report_test.txt`, `classes.json`
   - `training_curves_comparison.png`, `confusion_matrices_comparison.png`
   - `efficientnet_b0_dental.pt`
2. Only the **official** run goes into the repository, in `data/effnet_b0/`. Leave out the `.pt` file, which stays on Drive like the ResNet-50 weights. Agree on who commits, so that you do not both commit to the same folder.
3. Add the AI assistance to your **AI Use Log**.

## 8. Troubleshooting

| Message | Cause | Fix |
|---|---|---|
| `Manifest introuvable` | `eda_v2/` missing or at the wrong path | See section 2 of this guide |
| `… introuvable dans …/pr1` | A PR1 file is missing | Copy the team's `pr1/` folder |
| `Ordre des classes différent du PR1` / `Découpage différent du PR1` | Your manifest is not the team's manifest | Copy the team's `eda_v2/` folder; do not re-run notebook 01 |
| `Un fichier ne correspond plus au manifest` | The Kaggle dataset files differ from the manifest (MD5) | Stop and tell the team; do not continue |
| `Une autre règle est déjà enregistrée sur Drive` | A `comparison_rule.json` with other values already exists in `effnet_b0/` | Do not change the rule. Use an empty `effnet_b0/` folder |
| `CUDA out of memory` | GPU memory | Restart the runtime. Lowering `BATCH_SIZE` to 16 works, but it **changes the protocol**: write it down, because the comparison is then less fair |
| No GPU (`Appareil : cpu`) | GPU not enabled or Colab quota reached | Runtime > Change runtime type > T4 GPU, or try later |
