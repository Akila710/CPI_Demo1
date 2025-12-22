import os
import requests
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date
import sys

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE_DOCX = "assets/logos/templates/reference.docx"

AUTHOR = ""           # ✅ blank
VERSION = "Draft"
TODAY = date.today().isoformat()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE_NAME = os.getenv("PACKAGE_NAME")

if not PACKAGE_NAME:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(ARTIFACTS_DIR, PACKAGE_NAME)

if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# ---------------- FIND IFLOWS (CORRECT WAY) ----------------
iflows = [
    d for d in os.listdir(PACKAGE_PATH)
    if os.path.isdir(os.path.join(PACKAGE_PATH, d))
]

if not iflows:
    raise Exception(f"No iFlows found inside {PACKAGE_PATH}")

print(f"📦 Package: {PACKAGE_NAME}")
print(f"🔎 iFlows found: {iflows}")

# ---------------- GROQ SUMMARY ----------------
def groq_summary(iflow_name):
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
"""}
        }
    )

    return response.json()["choices"][0]["message"]["content"]

# ---------------- PROCESS EACH IFLOW ----------------
for iflow in iflows:
    iflow_path = os.path.join(PACKAGE_PATH, iflow)

    print(f"➡ Generating docs for iFlow: {iflow}")

    summary = groq_summary(iflow)

    # ---------- MARKDOWN (INSIDE IFLOW FOLDER) ----------
    md_path = os.path.join(iflow_path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {iflow}\n\n{summary}")

    # ---------- DOCX ----------
    doc = Document(TEMPLATE_DOCX)

    # Replace placeholders in COVER PAGE only
    for p in doc.paragraphs:
        p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
        p.text = p.text.replace("{{DATE}}", TODAY)
        p.text = p.text.replace("{{VERSION}}", VERSION)

    # Page break after cover
    doc.add_page_break()

    # Centered iFlow name
    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True

    # Add Groq content (SAME AS MD)
    for line in summary.split("\n"):
        doc.add_paragraph(line)

    docx_path = os.path.join(iflow_path, f"{iflow}.docx")
    doc.save(docx_path)

    print(f"✅ Generated: {md_path}, {docx_path}")

print("🎉 All iFlow documents generated successfully")
