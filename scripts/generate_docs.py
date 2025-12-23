import os
import requests
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
PACKAGE_NAME = os.getenv("PACKAGE_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TODAY = date.today().isoformat()
VERSION = "Draft"
AUTHOR = ""  # blank as requested

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = []

for item in os.listdir(PACKAGE_PATH):
    iflow_path = os.path.join(PACKAGE_PATH, item)
    if os.path.isdir(iflow_path):
        for root, _, files in os.walk(iflow_path):
            for f in files:
                if f.endswith(".iflw"):
                    iflows.append((item, os.path.join(root, f)))

if not iflows:
    raise Exception(f"No iFlows found inside {PACKAGE_PATH}")

print("Found iFlows:", [i[0] for i in iflows])

# ---------------- GROQ ----------------
def groq_summary(iflow_name, content):
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

File Content:
{content}
"""}
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# ---------------- GENERATE DOCS ----------------
for iflow_name, iflow_file in iflows:
    with open(iflow_file, encoding="utf-8", errors="ignore") as f:
        iflw_content = f.read()

    summary = groq_summary(iflow_name, iflw_content)

    IFLOW_DIR = os.path.join(PACKAGE_PATH, iflow_name)

    # -------- MARKDOWN --------
    md_path = os.path.join(IFLOW_DIR, f"{iflow_name}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow_name}\n\n{summary}")

    # -------- DOCX --------
    doc = Document()

    # Header logos (all pages)
    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    header_para.add_run().add_picture("assets/logos/templates/SAP.jpg", width=Inches(1))
    header_para.add_run("    ")
    header_para.add_run().add_picture("assets/logos/templates/mm_logo.png", width=Inches(1))

    # -------- PAGE 1 (Cover) --------
    title = doc.add_paragraph(iflow_name)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Inches(0.4)

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Author:"
    table.cell(0, 1).text = AUTHOR
    table.cell(1, 0).text = "Date:"
    table.cell(1, 1).text = TODAY
    table.cell(2, 0).text = "Version:"
    table.cell(2, 1).text = VERSION

    doc.add_page_break()

    # -------- PAGE 2 (TOC) --------
    doc.add_heading("Table of Contents", level=1)
    toc = [
        "1. Introduction",
        "1.1 Purpose",
        "1.2 Scope",
        "2. Integration Overview",
        "3. Integration Scenarios",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]
    for t in toc:
        doc.add_paragraph(t)

    doc.add_page_break()

    # -------- PAGE 3+ (IFLOW CONTENT) --------
    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(summary)

    doc_path = os.path.join(IFLOW_DIR, f"{iflow_name}.docx")
    doc.save(doc_path)

    print(f"✅ Generated docs inside {IFLOW_DIR}")

print("🎉 All iFlow documentation generated successfully")
