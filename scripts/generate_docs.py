import os
import requests
from datetime import date
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# ---------------- CONFIG ----------------
BASE_DIR = "cpi-artifacts"
PACKAGE = os.getenv("PACKAGE_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

TODAY = date.today().isoformat()
VERSION = "Draft"

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
def groq_summary(iflow_name, xml_text):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a SAP CPI Technical Architect."},
            {"role": "user", "content": f"""
Generate SAP CPI documentation text ONLY (no markdown symbols).
Provide sections:

1. Introduction
1.1 Purpose
1.2 Scope
2. Integration Overview
2.1 Integration Architecture
2.2 Integration Components (list sender, sender adapter, receiver, receiver adapter)
3. Integration Scenarios
3.1 Scenario Description
3.2 Data Flows
3.3 Security Requirements
4. Error Handling and Logging
5. Testing Validation
6. Reference Documents

iFlow Name: {iflow_name}

XML:
{xml_text}
"""}
        ]
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=120
    )

    return r.json()["choices"][0]["message"]["content"]

# ---------------- DOC HELPERS ----------------
def add_header(section):
    header = section.header
    header_para = header.paragraphs[0]

    run = header_para.add_run()
    run.add_picture(SAP_LOGO, width=Inches(1.2))

    header_para.add_run("\t" * 6)

    run2 = header_para.add_run()
    run2.add_picture(MM_LOGO, width=Inches(1.2))

def cover_page(doc, iflow_name):
    sec = doc.sections[0]
    add_header(sec)

    title = doc.add_paragraph(iflow_name)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(26)
    title.runs[0].bold = True

    doc.add_paragraph("\n")

    table = doc.add_table(rows=3, cols=2)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.style = "Table Grid"

    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = ""
    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = TODAY
    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = VERSION

    doc.add_page_break()

def toc_page(doc):
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
        "   3.2 Data Flows",
        "   3.3 Security Requirements",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]

    for line in toc:
        doc.add_paragraph(line)

    doc.add_page_break()

# ---------------- MAIN LOOP ----------------
for iflow in iflows:
    IFLOW_PATH = os.path.join(PACKAGE_PATH, iflow)
    xml_path = None

    for root, _, files in os.walk(IFLOW_PATH):
        for f in files:
            if f.endswith(".iflw"):
                xml_path = os.path.join(root, f)

    if not xml_path:
        print(f"⚠️ No .iflw found for {iflow}, skipping")
        continue

    xml = open(xml_path, encoding="utf-8").read()
    content = groq_summary(iflow, xml)

    # -------- MARKDOWN --------
    md_path = os.path.join(IFLOW_PATH, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(content)

    # -------- DOCX --------
    doc = Document()
    cover_page(doc, iflow)
    toc_page(doc)

    add_header(doc.sections[-1])

    for line in content.split("\n"):
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(6)

    docx_path = os.path.join(IFLOW_PATH, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Generated docs for {iflow}")

print("🎉 All iFlow documentation generated inside repo")
