import os
import requests
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

# ---------------- CONFIG ----------------
BASE_DIR = "cpi-artifacts"
SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

AUTHOR = ""
VERSION = "Draft"
TODAY = date.today().isoformat()

# ---------------- VALIDATION ----------------
if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(BASE_DIR, PACKAGE_NAME)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = []
for item in os.listdir(PACKAGE_PATH):
    iflow_path = os.path.join(PACKAGE_PATH, item)
    if os.path.isdir(iflow_path):
        iflows.append(item)

if not iflows:
    raise Exception("No iFlows found")

print(f"Found iFlows: {iflows}")

# ---------------- GROQ CALL ----------------
def groq_generate(iflow_name, iflw_content):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a SAP CPI Technical Architect. "
                    "Generate clean technical documentation in plain text ONLY. "
                    "Do NOT use markdown symbols like ## or **."
                )
            },
            {
                "role": "user",
                "content": f"""
Generate documentation with these sections:

1. Introduction
1.1 Purpose
1.2 Scope

2. Integration Overview
2.1 Integration Architecture
2.2 Integration Components (Sender, Receiver, Adapters)

3. Integration Scenarios
3.1 Scenario Description
3.2 Data Flows
3.3 Security Requirements

4. Error Handling and Logging
5. Testing Validation
6. Reference Documents

iFlow Name: {iflow_name}

iFlow Content:
{iflw_content}
"""
            }
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
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ---------------- DOCUMENT CREATION ----------------
for iflow in iflows:
    iflow_dir = os.path.join(PACKAGE_PATH, iflow)

    iflw_file = None
    for root, _, files in os.walk(iflow_dir):
        for f in files:
            if f.endswith(".iflw"):
                iflw_file = os.path.join(root, f)

    if not iflw_file:
        print(f"⚠️ No .iflw found for {iflow}, skipping")
        continue

    with open(iflw_file, encoding="utf-8") as f:
        iflw_content = f.read()

    content = groq_generate(iflow, iflw_content)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(iflow_dir, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"{iflow}\n\n{content}")

    # ---------- DOCX ----------
    doc = Document()

    # Header logos
    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    header_para.add_run().add_picture(SAP_LOGO, width=Inches(1))
    header_para.add_run("\t\t")
    header_para.add_run().add_picture(MM_LOGO, width=Inches(1))

    # Cover Page
    doc.add_paragraph("\n\n")
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(22)
    title.runs[0].bold = True

    doc.add_paragraph("\n")
    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = AUTHOR
    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = TODAY
    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = VERSION

    doc.add_page_break()

    # TOC Page (static)
    toc = doc.add_paragraph("Table of Contents")
    toc.runs[0].bold = True

    toc_items = [
        "1. Introduction",
        "    1.1 Purpose",
        "    1.2 Scope",
        "2. Integration Overview",
        "    2.1 Integration Architecture",
        "    2.2 Integration Components",
        "3. Integration Scenarios",
        "    3.1 Scenario Description",
        "    3.2 Data Flows",
        "    3.3 Security Requirements",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]

    for item in toc_items:
        doc.add_paragraph(item)

    doc.add_page_break()

    # Main Content
    for line in content.split("\n"):
        p = doc.add_paragraph(line)
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.")):
            p.runs[0].bold = True

    docx_path = os.path.join(iflow_dir, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Generated for {iflow}")

print("🎉 All iFlow documents generated successfully")
