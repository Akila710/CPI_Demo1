import os
import requests
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

# ---------------- CONFIG ----------------
BASE_DIR = "cpi-artifacts"
TEMPLATE_DOCX = "assets/logos/templates/reference.docx"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

MODEL = "llama-3.3-70b-versatile"

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(BASE_DIR, PACKAGE_NAME)

if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS ----------------
iflows = [
    d for d in os.listdir(PACKAGE_PATH)
    if os.path.isdir(os.path.join(PACKAGE_PATH, d))
]

if not iflows:
    raise Exception(f"No iFlows found inside {PACKAGE_PATH}")

print(f"Found iFlows: {iflows}")

# ---------------- GROQ FUNCTION ----------------
def groq_summary(iflow_name):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
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
            ]
        }
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    iflow_path = os.path.join(PACKAGE_PATH, iflow)

    print(f"Processing iFlow: {iflow}")

    summary = groq_summary(iflow)

    # ---------- MARKDOWN ----------
    md_path = os.path.join(iflow_path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow}\n\n{summary}")

    # ---------- DOCX ----------
    doc = Document(TEMPLATE_DOCX)

    # Clear template body but keep layout
    for p in doc.paragraphs[1:]:
        p.text = ""

    doc.add_page_break()

    # Centered iFlow name
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True

    doc.add_paragraph(summary)

    docx_path = os.path.join(iflow_path, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"Generated MD & DOCX for {iflow}")

print("🎉 All iFlow documents generated inside repo")
