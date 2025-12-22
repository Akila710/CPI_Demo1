import os
import requests
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import sys

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE_DOCX = "assets/logos/templates/reference.docx"
OUTPUT_DIR = "output"

AUTHOR = ""  # ✅ BLANK as requested
VERSION = "Draft"
TODAY = date.today().isoformat()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)

if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- FIND IFLOWS (FIXED) ----------------
iflows = []

for root, dirs, files in os.walk(PACKAGE_PATH):
    for file in files:
        if file.endswith(".xml") and "iflow" in root.lower():
            iflows.append(os.path.join(root, file))

if not iflows:
    raise Exception("No iFlows found")

print(f"Found iFlows: {iflows}")

# ---------------- GROQ CALL ----------------
def groq_summary(iflow_name, xml):
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
Generate SAP CPI technical documentation with:
- Purpose
- Sender / Receiver
- Adapters
- Flow Logic
- Error Handling

iFlow Name: {iflow_name}

XML:
{xml}
"""}
            ]
        }
    )

    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow_path in iflows:
    iflow_name = os.path.basename(os.path.dirname(iflow_path))
    xml = open(iflow_path, encoding="utf-8").read()

    summary = groq_summary(iflow_name, xml)

    # ---------- MARKDOWN ----------
    md_path = f"{OUTPUT_DIR}/{PACKAGE_NAME}_{iflow_name}.md"
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow_name}\n\n{summary}")

    # ---------- DOCX ----------
    doc = Document(TEMPLATE_DOCX)

    # Replace placeholders
    for p in doc.paragraphs:
        p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
        p.text = p.text.replace("{{DATE}}", TODAY)
        p.text = p.text.replace("{{VERSION}}", VERSION)

    # Add centered iFlow name (YOUR REQUIREMENT)
    doc.add_page_break()
    title = doc.add_paragraph(iflow_name)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True

    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(summary)

    docx_path = f"{OUTPUT_DIR}/{PACKAGE_NAME}_{iflow_name}.docx"
    doc.save(docx_path)

    print(f"Generated docs for iFlow: {iflow_name}")

print("✅ All iFlow documents generated")
