---
title: FabricAI Fabric Defect Inspection
emoji: 🧵
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# FabricAI Fabric Defect Inspection

Public demonstration of the FabricAI fabric inspection dashboard. The Docker
image runs the existing FastAPI backend and serves the HTML/CSS/JavaScript
frontend at the same URL. Inference runs on CPU hardware by default; expect
slower responses than a GPU workstation.

The detector and classification models are experimental. The FDD, TILDA, and
ZD001 classifier subsets are synthetic. Prediction confidence is not model
accuracy, and results are not validated for autonomous factory decisions.

This deployment bundle intentionally excludes source datasets, training
outputs, virtual environments, and redundant model checkpoints.
