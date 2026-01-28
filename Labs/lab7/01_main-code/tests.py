
# Chapter 7 - Lab 6a : Fine-tuning to follow instructions
#
# > Author : Badr TAJINI - Large Language model (LLMs) - ESIEE 2024-2025
#
# ---
# File for internal use (unit tests)


import subprocess


def test_gpt_class_finetune():
    command = ["python", "lab6/01_main-code/gpt_class_finetune.py", "--test_mode"]

    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, f"Script exited with errors: {result.stderr}"
