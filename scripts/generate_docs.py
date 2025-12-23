import os
import requests
from datetime import date
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ---------------- CONFIG ----------------
BASE_DIR = "cpi-artifacts"
PACKAGE = os.getenv("PACKAGE_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

TODAY = date.today().isoformat()

if not PACKAGE:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(BASE_DIR, PACKAGE)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = []
for item in os.listdir(PACKAGE_PATH):
    p = os.path.join(PACKAGE_PATH, item)
    if os.path.isdir(p):
        iflows.append(item)

if not iflows:
    raise Exception("No iFlows found")

print(f"Found iFlows: {iflows}")

# ---------------- GROQ ----------------
def groq_summary(iflow_name, content):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a SAP CPI Technical Architect."},
                {"role": "user", "content": f"""
Generate SAP CPI documentation content ONLY (no markdown symbols).

Provide content for:
1. Purpose
2. Scope
3. Integration Architecture
4. Integration Components (Sender, Receiver, Adapters)
5. Integration Scenario
6. Error Handling
7. Testing Validation

iFlow Name: {iflow_name}

iFlow File Content:
{content}
"""}
            ]
        }
    )
    return r.json()["choices"][0]["message"]["content"]

# ---------------- DOC CREATION ----------------
def create_doc(iflow_name, summary, out_path):
    doc = Document()

    # ---------- HEADER ----------
    section = doc.sections[0]
    header = section.header
    table = header.add_table(rows=1, cols=2, width=Inches(6))
    table.cell(0,0).paragraphs[0].add_run().add_picture(SAP_LOGO, width=Inches(1))
    table.cell(0,1).paragraphs[0].add_run().add_picture(MM_LOGO, width=Inches(1))
    table.cell(0,1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # ---------- PAGE 1 ----------
    title = doc.add_paragraph(iflow_name)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(22)

    doc.add_paragraph("\n")

    meta = doc.add_table(rows=3, cols=2)
    meta.style = "Table Grid"
    meta.cell(0,0).text = "Author:"
    meta.cell(0,1).text = ""
    meta.cell(1,0).text = "Date:"
    meta.cell(1,1).text = TODAY
    meta.cell(2,0).text = "Version:"
    meta.cell(2,1).text = "Draft"

    for row in meta.rows:
        for cell in row.cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # ---------- PAGE 2: TOC ----------
    doc.add_heading("Table of Contents", level=1)
    toc = [
        "1. Introduction",
        "   1.1 Purpose",
        "   1.2 Scope",
        "2. Integration Overview",
        "   2.1 Integration Architecture",
        "   2.2 Integration Components",
        "3. Integration Scenarios",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]
    for t in toc:
        doc.add_paragraph(t)

    doc.add_page_break()

    # ---------- PAGE 3+: CONTENT ----------
    doc.add_heading("1. Introduction", level=1)
    doc.add_heading("1.1 Purpose", level=2)
    doc.add_paragraph(summary)

    doc.save(out_path)

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    iflow_dir = os.path.join(PACKAGE_PATH, iflow)
    iflw_file = None

    for root, _, files in os.walk(iflow_dir):
        for f in files:
            if f.endswith(".iflw"):
                iflw_file = os.path.join(root, f)

    if not iflw_file:
        print(f"⚠️ No .iflw found in {iflow}, skipping")
        continue

    content = open(iflw_file, encoding="utf-8", errors="ignore").read()
    summary = groq_summary(iflow, content)

    # MD
    md_path = os.path.join(iflow_dir, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(summary)

    # DOCX
    docx_path = os.path.join(iflow_dir, f"{iflow}.docx")
    create_doc(iflow, summary, docx_path)

    print(f"✅ Generated for {iflow}")

print("🎉 All documents generated inside iFlow folders")
