
import sys
import builtins

inputs = ["law firms jacksonville fl", "10"]
input_index = [0]

def mock_input(prompt=""):
    if input_index[0] < len(inputs):
        value = inputs[input_index[0]]
        input_index[0] += 1
        return value
    return ""

builtins.input = mock_input

with open('final_competitor_profiler_COMPLETE.py', 'r', encoding='utf-8') as f:
    exec(f.read())
