import os
import requests
from datetime import date
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE = os.getenv("PACKAGE_NAME")

TODAY = date.today().isoformat()
VERSION = "Draft"

# ---------------- FIND IFLOWS ----------------
package_path = os.path.join(ARTIFACTS_DIR, PACKAGE)
iflows = [
    d for d in os.listdir(package_path)
    if os.path.isdir(os.path.join(package_path, d))
]

if not iflows:
    raise Exception(f"No iFlows found inside {package_path}")

# ---------------- GROQ CALL ----------------
def groq_generate(iflow):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a SAP CPI Technical Architect."},
            {"role": "user", "content": f"""
Generate clean SAP CPI documentation text with these sections ONLY:
1. Introduction
1.1 Purpose
1.2 Scope
2. Integration Overview
2.1 Integration Architecture
2.2 Integration Components (list sender, receiver, adapters)
3. Integration Scenarios
3.1 Scenario Description
4. Error Handling and Logging
5. Testing Validation
6. Reference Documents

NO markdown symbols.
NO bullets unless required.
iFlow name: {iflow}
"""}
        ]
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )
    return r.json()["choices"][0]["message"]["content"].strip()

# ---------------- DOC CREATION ----------------
for iflow in iflows:
    iflow_path = os.path.join(package_path, iflow)

    content = groq_generate(iflow)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(iflow_path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    # ---------- DOCX ----------
    doc = Document()

    # HEADER (logos once)
    section = doc.sections[0]
    header = section.header
    table = header.add_table(rows=1, cols=2)
    table.columns[0].width = Inches(3)
    table.columns[1].width = Inches(3)

    table.cell(0, 0).paragraphs[0].add_run().add_picture(SAP_LOGO, width=Inches(1))
    table.cell(0, 1).paragraphs[0].add_run().add_picture(MM_LOGO, width=Inches(1))
    table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # ---------- PAGE 1 ----------
    doc.add_paragraph("\n\n")
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(22)

    doc.add_paragraph("\n")

    info = doc.add_table(rows=3, cols=2)
    info.style = "Table Grid"
    info.cell(0, 0).text = "Author"
    info.cell(0, 1).text = ""
    info.cell(1, 0).text = "Date"
    info.cell(1, 1).text = TODAY
    info.cell(2, 0).text = "Version"
    info.cell(2, 1).text = VERSION

    for row in info.rows:
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # ---------- PAGE 2 TOC ----------
    doc.add_heading("Table of Contents", level=1)
    toc = [
        "1. Introduction",
        "   1.1 Purpose",
        "   1.2 Scope",
        "",
        "2. Integration Overview",
        "   2.1 Integration Architecture",
        "   2.2 Integration Components",
        "",
        "3. Integration Scenarios",
        "   3.1 Scenario Description",
        "",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]
    for line in toc:
        doc.add_paragraph(line)

    doc.add_page_break()

    # ---------- CONTENT ----------
    for block in content.split("\n\n"):
        p = doc.add_paragraph(block)
        if block[:2].isdigit():
            p.runs[0].bold = True

    doc_path = os.path.join(iflow_path, f"{iflow}.docx")
    doc.save(doc_path)

print("✅ Documents generated INSIDE each iFlow folder")
