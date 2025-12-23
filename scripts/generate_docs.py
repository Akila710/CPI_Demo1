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

AUTHOR = ""          # must be blank
VERSION = "Draft"
TODAY = date.today().isoformat()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS (CPI STRUCTURE) ----------------
iflows = [
    d for d in os.listdir(PACKAGE_PATH)
    if os.path.isdir(os.path.join(PACKAGE_PATH, d))
]

if not iflows:
    raise Exception(f"No iFlows found inside {PACKAGE_PATH}")

print(f"Found iFlows: {iflows}")

# ---------------- GROQ CALL ----------------
def groq_summary(iflow_name):
    response = requests.post(
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
Generate SAP CPI iFlow technical documentation with:
- Purpose
- Sender / Receiver
- Adapters
- Flow Logic
- Error Handling

iFlow Name: {iflow_name}
"""}
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    iflow_path = os.path.join(PACKAGE_PATH, iflow)

    print(f"📄 Generating docs for iFlow: {iflow}")

    summary = groq_summary(iflow)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(iflow_path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow}\n\n{summary}")

    # ---------- DOCX ----------
    doc = Document()

    # ===== HEADER (LOGOS) =====
    section = doc.sections[0]
    header = section.header

    header_table = header.add_table(rows=1, cols=2)
    header_table.autofit = False
    header_table.columns[0].width = Inches(3)
    header_table.columns[1].width = Inches(3)

    left = header_table.cell(0, 0).paragraphs[0]
    left.add_run().add_picture(SAP_LOGO, width=Inches(1.2))

    right = header_table.cell(0, 1).paragraphs[0]
    right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    right.add_run().add_picture(MM_LOGO, width=Inches(1.2))

    # ===== TITLE =====
    doc.add_paragraph("\n\n")
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.runs[0]
    run.bold = True
    run.font.size = Pt(20)

    doc.add_paragraph("\n")

    # ===== INFO TABLE =====
    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"

    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = AUTHOR

    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = TODAY

    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = VERSION

    # ===== PAGE 2: TOC =====
    doc.add_page_break()
    doc.add_heading("Table of Contents", level=1)

    toc_items = [
        "1. Introduction",
        "1.1 Purpose",
        "1.2 Scope",
        "2. Integration Overview",
        "2.1 Integration Architecture",
        "2.2 Integration Components",
        "3. Integration Scenarios",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]

    for item in toc_items:
        doc.add_paragraph(item)

    # ===== PAGE 3+: CONTENT =====
    doc.add_page_break()
    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(summary)

    docx_path = os.path.join(iflow_path, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Created: {md_path} and {docx_path}")

print("🎉 All iFlow documents generated successfully")
