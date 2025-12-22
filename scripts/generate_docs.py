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

AUTHOR = ""            # MUST BE BLANK
VERSION = "Draft"
TODAY = date.today().isoformat()

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)

if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOW FOLDERS ----------------
iflow_folders = [
    os.path.join(PACKAGE_PATH, d)
    for d in os.listdir(PACKAGE_PATH)
    if os.path.isdir(os.path.join(PACKAGE_PATH, d))
]

if not iflow_folders:
    raise Exception(f"No iFlow folders found inside {PACKAGE_PATH}")

print(f"Found iFlows: {[os.path.basename(i) for i in iflow_folders]}")

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
Generate SAP CPI iFlow technical documentation with sections:
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

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow_path in iflow_folders:
    iflow_name = os.path.basename(iflow_path)

    # find XML
    xml_files = [f for f in os.listdir(iflow_path) if f.endswith(".xml")]
    if not xml_files:
        print(f"⚠️ No XML found in {iflow_name}, skipping")
        continue

    xml_path = os.path.join(iflow_path, xml_files[0])
    xml = open(xml_path, encoding="utf-8").read()

    print(f"🔧 Processing iFlow: {iflow_name}")

    summary = groq_summary(iflow_name, xml)

    # ---------------- MARKDOWN ----------------
    md_path = os.path.join(iflow_path, f"{iflow_name}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow_name}\n\n{summary}")

    # ---------------- DOCX ----------------
    doc = Document(TEMPLATE_DOCX)

    # Replace cover placeholders ONLY
    for p in doc.paragraphs:
        p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
        p.text = p.text.replace("{{DATE}}", TODAY)
        p.text = p.text.replace("{{VERSION}}", VERSION)

    # REMOVE all body content after cover
    while len(doc.paragraphs) > 1:
        p = doc.paragraphs[-1]
        p._element.getparent().remove(p._element)

    # New page
    doc.add_page_break()

    # Centered iFlow title
    title = doc.add_paragraph(iflow_name)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True

    doc.add_paragraph(summary)

    docx_path = os.path.join(iflow_path, f"{iflow_name}.docx")
    doc.save(docx_path)

    print(f"✅ Generated: {md_path}, {docx_path}")

print("🎉 All iFlow documents generated successfully")
