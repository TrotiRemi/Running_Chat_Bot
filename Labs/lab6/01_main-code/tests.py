# Chapter 6 - Lab 5b : Fine-tuning for classification
# 
# > Author : Badr TAJINI - Large Language model (LLMs) - ESIEE 2024-2025
# 
# ---
#
# This file brings together all the relevant code we have covered so far from Labs 2 to 5.
# This file can be run as a standalone script.

# File for internal use (unit tests)


import subprocess


def test_gpt_class_finetune():
    command = ["python", "lab6/01_main-chapter-code/gpt_class_finetune.py", "--test_mode"]

    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, f"Script exited with errors: {result.stderr}"
