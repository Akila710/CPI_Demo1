import os
import requests
from docx import Document
from datetime import date
import sys

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE = "assets/logos/templates/reference.docx"
OUTPUT_DIR = "output"

AUTHOR = "Auto Generated"
VERSION = "1.0"
TODAY = date.today().isoformat()

package_name = os.getenv("PACKAGE_NAME")

if not package_name:
    print("❌ PACKAGE_NAME not provided")
    sys.exit(1)

pkg_path = os.path.join(ARTIFACTS_DIR, package_name)
iflows = [f for f in os.listdir(pkg_path) if f.endswith(".xml")]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def groq_summary(iflow, xml):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a SAP CPI Technical Architect."},
            {"role": "user", "content": f"""
Generate a concise SAP CPI technical summary with:
- Purpose
- Sender / Receiver
- Adapters
- Flow Logic
- Error Handling

iFlow Name: {iflow}
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

    return r.json()["choices"][0]["message"]["content"]

# ---------------- MARKDOWN ----------------
md_path = f"{OUTPUT_DIR}/{package_name}.md"
md = open(md_path, "w", encoding="utf-8")
md.write(f"# {package_name} – Technical Specification\n\n")

# ---------------- DOCX ----------------
doc = Document(TEMPLATE)
for p in doc.paragraphs:
    p.text = p.text.replace("{{PACKAGE_NAME}}", package_name)
    p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
    p.text = p.text.replace("{{DATE}}", TODAY)
    p.text = p.text.replace("{{VERSION}}", VERSION)

doc.add_page_break()
doc.add_heading("3. Integration Scenarios", level=1)

for iflow in iflows:
    path = os.path.join(pkg_path, iflow)
    xml = open(path, encoding="utf-8").read()

    summary = groq_summary(iflow, xml)

    md.write(f"## {iflow.replace('.xml','')}\n{summary}\n\n---\n")

    doc.add_heading(iflow.replace(".xml", ""), level=2)
    doc.add_paragraph(summary)

md.close()
doc.save(f"{OUTPUT_DIR}/{package_name}.docx")

print("✅ Documentation generated successfully")
