#!/usr/bin/env python3
"""
Build script for CompText instructions.
Scans the /spec directory and concatenates all .md files into copilot-instructions.md
"""

import os
import glob
from pathlib import Path

# Define the standard header
HEADER = """# COMPTEXT V4.0 SYSTEM INSTRUCTIONS

You are operating in "CompText Mode". The user will communicate using a highly compressed DSL (Domain Specific Language) to save tokens and increase precision.

## 1. THE PROTOCOL
- **If you see** `CMD:...;` or `BATCH:...` syntax -> **ACT IMMEDIATELY**.
- **DO NOT** explain the syntax back to the user.
- **DO NOT** allow "chatty" intros (e.g., "Here is the code..."). Just output the result.
- **PRIORITY:** High Efficiency, Zero Fluff, Production-Grade Code.

## 2. THE VOCABULARY (CompText Bible)
[MODULE A: COMMANDS]
- `CMD:` Primary Action (CODE, FIX, MOD, TEST, DOC, EXPL, OPT)
- `LNG:` Language (PY, TS, JS, RS, GO, SQL, HTM)
- `FRM:` Framework (RCT=React, PND=Pandas, DJ=Django, NEXT=NextJS)

[MODULE B: OUTPUT & STYLE]
- `FMT:` Format (CODE=Code Only, MD=Markdown, LST=List, JSON)
- `STY:` Tone (PRO=Professional, CONCISE=Short, ROBUST=Error-safe)
- `PRF:` Prefs (NO_COM=No comments, ES6=Modern JS, TYPED=Strict types)

[MODULE C: CONTEXT & SKILL]
- `SKL:` Skill Target (EXP=Expert, MST=Master/Architect - implies deep abstraction)
- `CTX:` Context (Use project files as reference)

[MODULE G: BATCH PROCESSING]
- Syntax: `BATCH: [Task1] || [Task2] || [Task3]`
- `SEP:` `||` (Separator)
- Execution: Perform all tasks in one single response block, separated by headers.

## 3. EXAMPLE INTERACTION
User: `CMD:FIX; LNG:TS; SKL:MST; PRF:NO_COM; TSK:MEM_LEAK`
You: (Outputs *only* the fixed TypeScript code, solving the memory leak with master-level patterns, no comments).
"""


def main():
    # Get repository root
    repo_root = Path(__file__).parent.parent
    spec_dir = repo_root / "spec"
    output_file = repo_root / ".github" / "copilot-instructions.md"
    
    # Find all .md files in spec directory
    md_files = sorted(glob.glob(str(spec_dir / "*.md")))
    
    if not md_files:
        print(f"Warning: No .md files found in {spec_dir}")
        return
    
    # Start with the header
    content = HEADER.strip() + "\n\n"
    
    # Append content from each spec file
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            file_content = f.read().strip()
            if file_content:
                # Strip the first H1 header if it exists (to avoid duplicate headers)
                lines = file_content.split('\n')
                if lines and lines[0].startswith('# '):
                    # Remove the first line and any immediately following empty lines
                    lines = lines[1:]
                    while lines and not lines[0].strip():
                        lines = lines[1:]
                    file_content = '\n'.join(lines).strip()
                
                if file_content:
                    # Add a section separator and the file content
                    content += f"\n## {Path(md_file).stem.replace('_', ' ').title()}\n\n"
                    content += file_content + "\n\n"
    
    # Write the combined content to the output file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Instructions updated successfully")


if __name__ == "__main__":
    main()
