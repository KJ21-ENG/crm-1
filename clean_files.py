import os
import re

files = [
    "docs/documentation creation task/01-tickets.md",
    "docs/documentation creation task/02-leads.md",
    "docs/documentation creation task/03-customers.md"
]

for fp in files:
    if os.path.exists(fp):
        with open(fp, "r") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if re.match(r'^Status:\s*completed', line):
                new_lines.append("Status: pending\n")
            elif "Screenshot Path:" in line or "Placement:" in line or "![Screenshot]" in line or "<figure>" in line:
                continue
            else:
                new_lines.append(line)
                
        with open(fp, "w") as f:
            f.writelines(new_lines)

# Remove screenshot directories
import shutil
dirs = [
    "docs/documentation creation task screenshots/01-tickets",
    "docs/documentation creation task screenshots/02-leads",
    "docs/documentation creation task screenshots/03-customers"
]
for d in dirs:
    if os.path.exists(d):
        shutil.rmtree(d)

print("Files cleaned and screenshot directories removed.")
