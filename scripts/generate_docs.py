import os
import requests
from docx import Document
from datetime import date

# ---------- CONFIG ----------
ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE = "assets/logos/templates/reference.docx"
OUTPUT_DIR = "output"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

AUTHOR = "Auto Generated"
VERSION = "Draft"
TODAY = date.today().isoformat()

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- GROQ ----------
def generate_summary(iflow_name, xml):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a SAP CPI Technical Architect."},
            {"role": "user", "content": f"""
Generate a SAP CPI technical summary with:
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
        json=payload,
        timeout=60
    )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ---------- MAIN ----------
package_path = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)
iflows = [f for f in os.listdir(package_path) if f.endswith(".xml")]

for iflow in iflows:
    iflow_name = iflow.replace(".xml", "")
    xml_path = os.path.join(package_path, iflow)
    xml = open(xml_path, encoding="utf-8").read()

    print(f"🔹 Processing iFlow: {iflow_name}")

    summary = generate_summary(iflow_name, xml)

    # -------- MARKDOWN --------
    md_path = f"{OUTPUT_DIR}/{iflow_name}.md"
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow_name}\n\n")
        md.write(summary)

    # -------- DOCX --------
    doc = Document(TEMPLATE)

    for p in doc.paragraphs:
        p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
        p.text = p.text.replace("{{DATE}}", TODAY)
        p.text = p.text.replace("{{VERSION}}", VERSION)
        p.text = p.text.replace("{{IFLOW_NAME}}", iflow_name)

    doc.add_page_break()

    doc.add_heading("1. Integration Scenario", level=1)
    doc.add_paragraph(summary)

    out_doc = f"{OUTPUT_DIR}/{iflow_name}.docx"
    doc.save(out_doc)

    print(f"✅ Generated: {out_doc}")

print("🎉 All iFlow documents generated")
