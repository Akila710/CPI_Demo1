import os
import requests
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PACKAGE = os.getenv("PACKAGE_NAME")

BASE = f"cpi-artifacts/{PACKAGE}"
TODAY = date.today().isoformat()
VERSION = "Draft"

def groq_summary(iflow_name, iflw_path):
    content = open(iflw_path, encoding="utf-8", errors="ignore").read()

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an SAP CPI Integration Architect. Respond in plain text only."},
            {"role": "user", "content": f"""
Generate clean SAP CPI documentation (NO markdown symbols).

Sections:
1. Introduction
1.1 Purpose
1.2 Scope
2. Integration Overview
2.1 Integration Architecture
2.2 Integration Components (list sender, receiver, adapters if known)
3. Integration Scenarios
3.1 Scenario Description
4. Error Handling and Logging
5. Testing Validation
6. Reference Documents

iFlow name: {iflow_name}

Definition:
{content}
"""}
        ]
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    return r.json()["choices"][0]["message"]["content"]

def add_logos(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    run.add_picture("assets/logos/SAP.png", width=Inches(1.2))
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    p2 = doc.add_paragraph()
    run2 = p2.add_run()
    run2.add_picture("assets/logos/motiveminds.png", width=Inches(1.5))
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT

def add_title_page(doc, iflow):
    add_logos(doc)

    title = doc.add_paragraph(iflow)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(22)

    doc.add_paragraph("")

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0,0).text = "Author:"
    table.cell(0,1).text = ""
    table.cell(1,0).text = "Date:"
    table.cell(1,1).text = TODAY
    table.cell(2,0).text = "Version:"
    table.cell(2,1).text = VERSION

    doc.add_page_break()

def add_toc(doc):
    add_logos(doc)
    toc = doc.add_paragraph("Table of Contents")
    toc.runs[0].bold = True
    toc.runs[0].font.size = Pt(14)

    items = [
        "1. Introduction",
        "   1.1 Purpose",
        "   1.2 Scope",
        "2. Integration Overview",
        "   2.1 Integration Architecture",
        "   2.2 Integration Components",
        "3. Integration Scenarios",
        "   3.1 Scenario Description",
        "4. Error Handling and Logging",
        "5. Testing Validation",
        "6. Reference Documents"
    ]

    for i in items:
        doc.add_paragraph(i)

    doc.add_page_break()

def add_content(doc, text):
    add_logos(doc)
    for line in text.split("\n"):
        p = doc.add_paragraph(line)
        if line.strip() and line[0].isdigit():
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(12)

for iflow in os.listdir(BASE):
    path = os.path.join(BASE, iflow)
    if not os.path.isdir(path):
        continue

    iflw = None
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".iflw"):
                iflw = os.path.join(root, f)

    if not iflw:
        continue

    summary = groq_summary(iflow, iflw)

    # MARKDOWN
    md_path = os.path.join(path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(summary)

    # DOCX
    doc = Document()
    add_title_page(doc, iflow)
    add_toc(doc)
    add_content(doc, summary)

    doc.save(os.path.join(path, f"{iflow}.docx"))

print("✅ Documentation generated correctly")
