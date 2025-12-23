import os
from datetime import date
import requests
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ---------------- CONFIG ----------------
BASE_DIR = "cpi-artifacts"
PACKAGE = os.getenv("PACKAGE_NAME")
GROQ_KEY = os.getenv("GROQ_API_KEY")

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

TODAY = date.today().isoformat()

if not PACKAGE:
    raise Exception("PACKAGE_NAME not set")

PKG_PATH = os.path.join(BASE_DIR, PACKAGE)
if not os.path.isdir(PKG_PATH):
    raise Exception(f"Package not found: {PKG_PATH}")

# ---------------- GROQ ----------------
def groq(text):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a SAP CPI Technical Architect."},
                {"role": "user", "content": text}
            ]
        }
    )
    return r.json()["choices"][0]["message"]["content"]

# ---------------- HELPERS ----------------
def add_header(doc):
    section = doc.sections[0]
    header = section.header
    header.paragraphs[0].clear()

    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run().add_picture(SAP_LOGO, width=Inches(1.2))

    p = header.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.add_run().add_picture(MM_LOGO, width=Inches(1.2))

def title_page(doc, iflow):
    add_header(doc)

    doc.add_paragraph("\n\n")
    t = doc.add_paragraph(iflow)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.runs[0].font.size = Pt(24)
    t.runs[0].bold = True

    doc.add_paragraph("\n")

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0,0).text = "Author"
    table.cell(0,1).text = ""
    table.cell(1,0).text = "Date"
    table.cell(1,1).text = TODAY
    table.cell(2,0).text = "Version"
    table.cell(2,1).text = "Draft"

    doc.add_page_break()

def toc_page(doc):
    add_header(doc)
    doc.add_heading("Table of Contents", level=1)

    toc = [
        "1. Introduction",
        "   1.1 Purpose",
        "   1.2 Scope",
        "2. Integration Overview",
        "   2.1 Integration Architecture",
        "   2.2 Integration Components",
        "3. Integration Scenarios",
        "   3.1 Scenario Description",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]
    for line in toc:
        doc.add_paragraph(line)

    doc.add_page_break()

# ---------------- MAIN ----------------
for iflow in os.listdir(PKG_PATH):
    IFLOW_PATH = os.path.join(PKG_PATH, iflow)
    if not os.path.isdir(IFLOW_PATH):
        continue

    print(f"Processing iFlow: {iflow}")

    doc = Document()
    title_page(doc, iflow)
    toc_page(doc)

    add_header(doc)

    content = groq(f"""
Generate SAP CPI documentation with numbered sections:
1. Introduction
1.1 Purpose
1.2 Scope
2. Integration Overview
2.1 Integration Architecture
2.2 Integration Components (give sender/receiver/adapters)
3. Integration Scenarios
3.1 Scenario Description
4. Error Handling and Logging
5. Testing Validation
6. Reference Documents

No markdown symbols.
iFlow: {iflow}
""")

    for line in content.split("\n"):
        doc.add_paragraph(line)

    out_doc = os.path.join(IFLOW_PATH, f"{iflow}.docx")
    out_md = os.path.join(IFLOW_PATH, f"{iflow}.md")

    doc.save(out_doc)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated inside {IFLOW_PATH}")

print("DONE")
