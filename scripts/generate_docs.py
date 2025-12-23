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

AUTHOR = ""            # blank as requested
VERSION = "Draft"
TODAY = date.today().isoformat()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = []
for name in os.listdir(PACKAGE_PATH):
    path = os.path.join(PACKAGE_PATH, name)
    if os.path.isdir(path):
        iflows.append(name)

if not iflows:
    raise Exception(f"No iFlows found inside {PACKAGE_PATH}")

print("Found iFlows:", iflows)

# ---------------- GROQ ----------------
def groq_summary(iflow_name, iflw_text):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a SAP CPI Technical Architect."
            },
            {
                "role": "user",
                "content": f"""
Generate SAP CPI technical documentation with sections:
Purpose
Sender / Receiver
Adapters
Flow Logic
Error Handling

iFlow Name: {iflow_name}

iFlow Definition:
{iflw_text}
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
        json=payload,
        timeout=60
    )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    IFLOW_PATH = os.path.join(PACKAGE_PATH, iflow)

    iflw_file = os.path.join(
        IFLOW_PATH,
        "src/main/resources/scenarioflows/integrationflow",
        f"{iflow}.iflw"
    )

    if not os.path.isfile(iflw_file):
        print(f"⚠️ No .iflw found for {iflow}, skipping")
        continue

    with open(iflw_file, encoding="utf-8", errors="ignore") as f:
        iflw_text = f.read()

    summary = groq_summary(iflow, iflw_text)

    # ================= MARKDOWN =================
    md_path = os.path.join(IFLOW_PATH, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow}\n\n{summary}")

    # ================= DOCX =================
    doc = Document()

    # ---------- HEADER (ALL PAGES) ----------
    section = doc.sections[0]
    header = section.header
    header_p = header.paragraphs[0]
    header_p.clear()

    header_p.add_run().add_picture(SAP_LOGO, width=Inches(1.2))
    header_p.add_run("\t\t")
    header_p.add_run().add_picture(MM_LOGO, width=Inches(1.2))
    header_p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # ---------- PAGE 1 ----------
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(22)
    title.runs[0].bold = True

    doc.add_paragraph("\n")

    table = doc.add_table(rows=3, cols=2)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = AUTHOR
    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = TODAY
    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = VERSION

    doc.add_page_break()

    # ---------- PAGE 2: TOC ----------
    doc.add_heading("Table of Contents", level=1)
    toc = [
        "1. Introduction",
        "1.1 Purpose",
        "1.2 Scope",
        "2. Integration Overview",
        "3. Integration Scenarios",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents",
    ]
    for t in toc:
        doc.add_paragraph(t)

    doc.add_page_break()

    # ---------- PAGE 3+: CONTENT ----------
    doc.add_heading("1. Introduction", level=1)
    for line in summary.split("\n"):
        doc.add_paragraph(line)

    docx_path = os.path.join(IFLOW_PATH, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Generated for {iflow}")

print("🎉 All iFlow documents generated successfully")
