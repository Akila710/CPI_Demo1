import os
import requests
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

TODAY = date.today().isoformat()

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = []
for root, _, files in os.walk(PACKAGE_PATH):
    for f in files:
        if f.endswith(".xml"):
            iflows.append(os.path.join(root, f))

if not iflows:
    raise Exception(f"No iFlows found inside {PACKAGE_PATH}")

# ---------------- GROQ ----------------
def groq_generate(iflow_name, xml):
    r = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a SAP CPI Technical Architect."},
                {"role": "user", "content": f"""
Generate SAP CPI documentation with sections:
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

For iFlow: {iflow_name}

XML:
{xml}
"""}
            ]
        }
    )
    return r.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow_xml in iflows:
    iflow_dir = os.path.dirname(iflow_xml)
    iflow_name = os.path.basename(iflow_dir)

    xml = open(iflow_xml, encoding="utf-8").read()
    content = groq_generate(iflow_name, xml)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(iflow_dir, f"{iflow_name}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow_name}\n\n")
        md.write(content)

    # ---------- DOCX ----------
    doc = Document()

    # ---- HEADER (logos on every page) ----
    section = doc.sections[0]
    header = section.header
    header_p = header.paragraphs[0]
    header_p.add_run().add_picture("assets/logos/templates/SAP.jpg", width=Inches(1.2))
    header_p.add_run("\t\t")
    header_p.add_run().add_picture("assets/logos/templates/mm_logo.png", width=Inches(1.2))

    # ---- PAGE 1: COVER ----
    title = doc.add_paragraph(iflow_name)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = ""
    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = TODAY
    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = "Draft"

    doc.add_page_break()

    # ---- PAGE 2: TOC (STATIC) ----
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
        "6. Reference Documents"
    ]
    for item in toc_items:
        doc.add_paragraph(item)

    doc.add_page_break()

    # ---- PAGE 3+: ACTUAL CONTENT ----
    for line in content.split("\n"):
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.")):
            doc.add_heading(line.strip(), level=1)
        else:
            doc.add_paragraph(line)

    docx_path = os.path.join(iflow_dir, f"{iflow_name}.docx")
    doc.save(docx_path)

    print(f"✅ Generated for iFlow: {iflow_name}")

print("🎉 All iFlow documents generated successfully")
