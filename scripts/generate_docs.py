import os
import requests
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

# ---------------- CONFIG ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE = "assets/logos/templates/reference.docx"

AUTHOR = "Auto Generated"
VERSION = "Draft"
TODAY = date.today().isoformat()

pkg_path = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)

if not os.path.isdir(pkg_path):
    raise Exception(f"Package not found: {pkg_path}")

iflows = [f for f in os.listdir(pkg_path) if f.endswith(".xml")]

if not iflows:
    raise Exception("No iFlows found")

# ---------------- GROQ CALL ----------------
def generate_summary(iflow_name, xml):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a SAP CPI Technical Architect."},
            {"role": "user", "content": f"""
Generate SAP CPI iFlow documentation with:
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

    r = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    iflow_name = iflow.replace(".xml", "")
    xml_path = os.path.join(pkg_path, iflow)
    xml_content = open(xml_path, encoding="utf-8").read()

    print(f"📄 Generating docs for {iflow_name}")

    summary = generate_summary(iflow_name, xml_content)

    # -------- MARKDOWN --------
    md_path = os.path.join(pkg_path, f"{iflow_name}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow_name}\n\n")
        md.write(summary)

    # -------- DOCX --------
    doc = Document(TEMPLATE)

    # Replace placeholders
    for p in doc.paragraphs:
        p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
        p.text = p.text.replace("{{DATE}}", TODAY)
        p.text = p.text.replace("{{VERSION}}", VERSION)

    # 👉 ADD IFLOW NAME AT CENTER (FIRST PAGE)
    title = doc.add_paragraph(iflow_name)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = 240000  # 24pt

    doc.add_page_break()

    doc.add_heading("Integration Scenario", level=1)
    doc.add_paragraph(summary)

    docx_path = os.path.join(pkg_path, f"{iflow_name}.docx")
    doc.save(docx_path)

    print(f"✅ Generated {iflow_name}.docx and .md")
