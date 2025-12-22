import os
import requests
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE_DOCX = "assets/logos/templates/reference.docx"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

AUTHOR = ""        # MUST BE BLANK
VERSION = "Draft"
TODAY = date.today().isoformat()

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)

if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOW FOLDERS ----------------
iflow_dirs = [
    d for d in os.listdir(PACKAGE_PATH)
    if os.path.isdir(os.path.join(PACKAGE_PATH, d))
]

if not iflow_dirs:
    raise Exception(f"No iFlow folders found inside {PACKAGE_PATH}")

print(f"Found iFlows: {iflow_dirs}")

# ---------------- GROQ SUMMARY ----------------
def groq_summary(iflow_name, xml_content):
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a SAP CPI Technical Architect."
            },
            {
                "role": "user",
                "content": f"""
Generate SAP CPI iFlow technical documentation with:
- Purpose
- Sender / Receiver
- Adapters
- Flow Logic
- Error Handling

iFlow Name: {iflow_name}

XML:
{xml_content}
"""
            }
        ]
    }

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflow_dirs:
    iflow_path = os.path.join(PACKAGE_PATH, iflow)

    # find xml inside iflow folder
    xml_files = [f for f in os.listdir(iflow_path) if f.endswith(".xml")]

    if not xml_files:
        print(f"⚠️ No XML found in {iflow}, skipping")
        continue

    xml_path = os.path.join(iflow_path, xml_files[0])
    xml_content = open(xml_path, encoding="utf-8").read()

    print(f"📄 Generating docs for iFlow: {iflow}")

    summary = groq_summary(iflow, xml_content)

    # ---------------- MARKDOWN ----------------
    md_path = os.path.join(iflow_path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow}\n\n{summary}")

    # ---------------- DOCX ----------------
    doc = Document(TEMPLATE_DOCX)

    # Replace only placeholders (structure remains)
    for p in doc.paragraphs:
        p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
        p.text = p.text.replace("{{DATE}}", TODAY)
        p.text = p.text.replace("{{VERSION}}", VERSION)
        p.text = p.text.replace("{{PACKAGE_NAME}}", PACKAGE_NAME)

    # New page for iFlow content
    doc.add_page_break()

    # Centered iFlow name
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.runs[0]
    run.bold = True

    # Add Groq content
    for line in summary.split("\n"):
        doc.add_paragraph(line)

    docx_path = os.path.join(iflow_path, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Generated inside {iflow_path}")

print("🎉 All iFlow documents generated successfully")
