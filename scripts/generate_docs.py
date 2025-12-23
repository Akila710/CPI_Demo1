import os
import requests
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches
from datetime import date

# ---------------- CONFIG ----------------
BASE_DIR = "cpi-artifacts"
PACKAGE = os.getenv("PACKAGE_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

MODEL = "llama-3.3-70b-versatile"

if not PACKAGE:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(BASE_DIR, PACKAGE)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = [
    d for d in os.listdir(PACKAGE_PATH)
    if os.path.isdir(os.path.join(PACKAGE_PATH, d))
]

if not iflows:
    raise Exception(f"No iFlows found inside {PACKAGE_PATH}")

print("Found iFlows:", iflows)

# ---------------- GROQ ----------------
def groq_summary(iflow_name):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a SAP CPI Technical Architect."},
                {"role": "user", "content": f"""
Generate SAP CPI iFlow documentation with these sections ONLY:

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
"""}
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    iflow_path = os.path.join(PACKAGE_PATH, iflow)

    summary = groq_summary(iflow)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(iflow_path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow}\n\n{summary}")

    # ---------- DOCX ----------
    doc = Document()

    # Header with logos
    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    header_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header_para.add_run().add_picture(SAP_LOGO, width=Inches(1))

    header_para.add_run("\t\t\t")
    header_para.add_run().add_picture(MM_LOGO, width=Inches(1))

    # Page 1 – Title
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True

    # Author table
    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = ""
    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = date.today().isoformat()
    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = "Draft"

    doc.add_page_break()

    # Page 2 – TOC (STATIC)
    doc.add_heading("Table of Contents", level=1)
    toc_items = [
        "1. Introduction",
        "1.1 Purpose",
        "1.2 Scope",
        "2. Integration Overview",
        "2.1 Integration Architecture",
        "2.2 Integration Components",
        "3. Integration Scenarios",
        "3.1 Scenario Description",
        "3.2 Data Flows",
        "3.3 Security Requirements",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents",
    ]
    for item in toc_items:
        doc.add_paragraph(item)

    doc.add_page_break()

    # Page 3+ – CONTENT (SAME AS MD)
    for line in summary.split("\n"):
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.")):
            doc.add_heading(line.strip(), level=1)
        else:
            doc.add_paragraph(line)

    docx_path = os.path.join(iflow_path, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"Generated docs for {iflow}")
