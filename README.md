# Reconnaissance Blind Chess — Execution Guide

This repository contains multiple agents designed to play Reconnaissance Blind Chess (RBC).

## 📁 Project Structure

RECONNAISSANCE-BLIND-CHESS/
├── Part4/
│   ├── ImprovedAgent.py
│   ├── RandomSensing.py
│   ├── ...

## ▶️ Running a Single Match

To run a one-on-one match between two agents (e.g. `ImprovedAgent.py` vs `RandomSensing.py`):

cd RECONNAISSANCE-BLIND-CHESS
rc-bot-match Part4\ImprovedAgent.py Part4\RandomSensing.py

## 🔁 Running a Round-Robin Tournament

To execute a round-robin tournament involving multiple bots:

1. Navigate to the project directory:

cd RECONNAISSANCE-BLIND-CHESS

2. Run the RR script:

python RR.py


This will automatically match each bot against every other bot twice—once as White and once as Black—and print the final statistics.
