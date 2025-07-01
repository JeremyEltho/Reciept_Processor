import os
import sys
import subprocess

# Ensure results folders exist
for sub in ["results/single", "results/events", "results/batch"]:
    os.makedirs(sub, exist_ok=True)

# Clean results folders before each run
for sub in ["results/single", "results/events", "results/batch"]:
    for f in os.listdir(sub):
        fp = os.path.join(sub, f)
        if os.path.isfile(fp):
            os.remove(fp)

# Build the command to run the unified script
args = sys.argv[1:]
cmd = [sys.executable, "receipt_processor.py"] + args

# Run the main script
subprocess.run(cmd)

print("\nResults saved to:")
print("   Single receipts: results/single/")
print("   Event processing: results/events/")
print("   Batch processing: results/batch/")
