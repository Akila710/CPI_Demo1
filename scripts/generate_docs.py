import os
import requests
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import subprocess

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
PACKAGE = os.getenv("PACKAGE_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

TODAY = date.today().isoformat()
VERSION = "Draft"

# ---------------- VALIDATION ----------------
if not PACKAGE:
    raise Exception("PACKAGE_NAME not provided")

PKG_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE)
if not os.path.isdir(PKG_PATH):
    raise Exception(f"Package not found: {PKG_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = []
for name in os.listdir(PKG_PATH):
    iflow_path = os.path.join(PKG_PATH, name)
    if os.path.isdir(iflow_path):
        iflows.append(name)

if not iflows:
    raise Exception(f"No iFlows found inside {PKG_PATH}")

print("Found iFlows:", iflows)

# ---------------- GROQ ----------------
def groq_generate(iflow_name, iflw_path):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a SAP CPI Technical Architect. "
                    "Return clean professional text only. "
                    "Do NOT use markdown, symbols, bullets, or special characters. "
                    "Use numbered section titles exactly as requested."
                )
            },
            {
                "role": "user",
                "content": f"""
Generate content for these sections:

1. Introduction
1.1 Purpose
1.2 Scope
2. Integration Overview
2.1 Integration Architecture
2.2 Integration Components
3. Integration Scenarios
3.1 Scenario Description
3.2 Data Flows
3.3 Security Requirements
4. Error Handling and Logging
5. Testing Validation
6. Reference Documents

iFlow Name: {iflow_name}
"""
            }
        ]
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    return r.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    IFLOW_DIR = os.path.join(PKG_PATH, iflow)
    IFLOW_FILE = os.path.join(
        IFLOW_DIR,
        "src/main/resources/scenarioflows/integrationflow",
        f"{iflow}.iflw"
    )

    if not os.path.exists(IFLOW_FILE):
        print(f"⚠️ {iflow}.iflw not found, skipping")
        continue

    content = groq_generate(iflow, IFLOW_FILE)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(IFLOW_DIR, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    # ---------- DOCX ----------
    doc = Document()

    # Header (logos on every page)
    section = doc.sections[0]
    header = section.header
    p = header.paragraphs[0]
    p.clear()

    p.add_run().add_picture(SAP_LOGO, width=Inches(1))
    p.add_run("\t" * 6)
    p.add_run().add_picture(MM_LOGO, width=Inches(1))

    # ---------- COVER PAGE ----------
    doc.add_paragraph("\n\n")
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(20)

    doc.add_paragraph("\n")

    table = doc.add_table(rows=3, cols=2)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = ""
    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = TODAY
    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = VERSION

    doc.add_page_break()

    # ---------- TOC PAGE ----------
    toc = doc.add_heading("Table of Contents", level=1)
    toc.alignment = WD_ALIGN_PARAGRAPH.LEFT

    toc_items = [
        "1. Introduction",
        "   1.1 Purpose",
        "   1.2 Scope",
        "2. Integration Overview",
        "   2.1 Integration Architecture",
        "   2.2 Integration Components",
        "3. Integration Scenarios",
        "   3.1 Scenario Description",
        "   3.2 Data Flows",
        "   3.3 Security Requirements",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents",
    ]

    for i in toc_items:
        doc.add_paragraph(i)

    doc.add_page_break()

    # ---------- CONTENT ----------
    for line in content.split("\n"):
        if line.strip().startswith(tuple(str(i) for i in range(1, 7))):
            doc.add_heading(line.strip(), level=1)
        else:
            doc.add_paragraph(line)

    docx_path = os.path.join(IFLOW_DIR, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Generated docs for {iflow}")

# ---------------- COMMIT BACK ----------------
subprocess.run(["git", "config", "user.name", "github-actions"])
subprocess.run(["git", "config", "user.email", "actions@github.com"])
subprocess.run(["git", "add", ARTIFACTS_DIR])
subprocess.run(["git", "commit", "-m", "Auto-generate iFlow documentation"])
subprocess.run(["git", "push"])
