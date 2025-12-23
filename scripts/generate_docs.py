import os
import time
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

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

# ---------------- VALIDATION ----------------
if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(BASE_DIR, PACKAGE_NAME)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = [
    name for name in os.listdir(PACKAGE_PATH)
    if os.path.isdir(os.path.join(PACKAGE_PATH, name))
]

if not iflows:
    raise Exception("No iFlows found")

print(f"Found iFlows: {iflows}")

# ---------------- GROQ CALL (WITH RETRY) ----------------
def groq_generate(iflow_name, iflw_content, retries=3):
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a SAP CPI Technical Architect. "
                    "Generate clean technical documentation in plain text ONLY. "
                    "Do NOT use markdown symbols like ##, **, -, or bullets. "
                    "Use numbered headings exactly as provided."
                )
            },
            {
                "role": "user",
                "content": f"""
Generate documentation strictly with these numbered sections:

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

Base everything ONLY on the iFlow content.

iFlow Name:
{iflow_name}

iFlow Content:
{iflw_content}
"""
            }
        ]
    }

    for attempt in range(retries):
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        if response.status_code == 429:
            wait = 10 + attempt * 10
            print(f"⚠️ Rate limit hit. Waiting {wait}s before retry...")
            time.sleep(wait)
            continue

        response.raise_for_status()

    raise Exception("Groq API failed after retries")

# ---------------- DOCUMENT CREATION ----------------
for iflow in iflows:
    print(f"▶ Processing iFlow: {iflow}")
    iflow_dir = os.path.join(PACKAGE_PATH, iflow)

    iflw_file = None
    for root, _, files in os.walk(iflow_dir):
        for f in files:
            if f.endswith(".iflw"):
                iflw_file = os.path.join(root, f)
                break

    if not iflw_file:
        print(f"⚠️ No .iflw found for {iflow}, skipping")
        continue

    with open(iflw_file, encoding="utf-8", errors="ignore") as f:
        iflw_content = f.read()

    content = groq_generate(iflow, iflw_content)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(iflow_dir, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(content)

    # ---------- DOCX ----------
    doc = Document()

    # Header (logos ONCE)
    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    header_para.clear()

    run = header_para.add_run()
    run.add_picture(SAP_LOGO, width=Inches(1.1))
    header_para.add_run("\t\t\t")
    run2 = header_para.add_run()
    run2.add_picture(MM_LOGO, width=Inches(1.0))

    # Title page
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(22)
    title.runs[0].bold = True

    doc.add_paragraph()

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Author"
    table.cell(0, 1).text = AUTHOR
    table.cell(1, 0).text = "Date"
    table.cell(1, 1).text = TODAY
    table.cell(2, 0).text = "Version"
    table.cell(2, 1).text = VERSION

    doc.add_page_break()

    # Main content
    for line in content.split("\n"):
        p = doc.add_paragraph(line.strip())
        if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.")):
            p.runs[0].bold = True

    docx_path = os.path.join(iflow_dir, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Generated docs inside {iflow_dir}")

    # IMPORTANT: pause between iFlows
    time.sleep(8)

print("🎉 All iFlow documents generated successfully")
