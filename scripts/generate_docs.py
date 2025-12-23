import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from datetime import date

# ---------------- CONFIG ----------------
PACKAGE = os.getenv("PACKAGE_NAME")
BASE = f"cpi-artifacts/{PACKAGE}"

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

TODAY = date.today().isoformat()
VERSION = "Draft"

# ---------------- HEADER (ONCE) ----------------
def add_header(doc):
    section = doc.sections[0]
    header = section.header

    # clear existing
    for p in header.paragraphs:
        p.clear()

    table = header.add_table(rows=1, cols=2, width=Inches(6))
    left, right = table.rows[0].cells

    lp = left.paragraphs[0]
    lp.add_run().add_picture(SAP_LOGO, width=Inches(1.2))
    lp.alignment = WD_ALIGN_PARAGRAPH.LEFT

    rp = right.paragraphs[0]
    rp.add_run().add_picture(MM_LOGO, width=Inches(1.2))
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# ---------------- TITLE PAGE ----------------
def title_page(doc, iflow):
    p = doc.add_paragraph()
    run = p.add_run(iflow)
    run.bold = True
    run.font.size = Pt(20)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("\n")

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"

    table.cell(0,0).text = "Author"
    table.cell(0,1).text = ""
    table.cell(1,0).text = "Date"
    table.cell(1,1).text = TODAY
    table.cell(2,0).text = "Version"
    table.cell(2,1).text = VERSION

    doc.add_page_break()

# ---------------- TOC PAGE ----------------
def toc_page(doc):
    p = doc.add_paragraph("Table of Contents")
    p.runs[0].bold = True

    toc = [
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

    for line in toc:
        doc.add_paragraph(line)

    doc.add_page_break()

# ---------------- CONTENT ----------------
def content(doc, iflow):
    doc.add_heading("1. Introduction", level=1)
    doc.add_heading("1.1 Purpose", level=2)
    doc.add_paragraph(
        f"The purpose of {iflow} is to integrate source and target systems using SAP CPI."
    )

    doc.add_heading("1.2 Scope", level=2)
    doc.add_paragraph(
        "This document covers architecture, components, scenarios, and error handling."
    )

    doc.add_heading("2. Integration Overview", level=1)
    doc.add_heading("2.1 Integration Architecture", level=2)
    doc.add_paragraph(
        "The integration architecture consists of sender, CPI runtime, and receiver."
    )

    doc.add_heading("2.2 Integration Components", level=2)
    table = doc.add_table(rows=2, cols=2)
    table.style = "Table Grid"
    table.cell(0,0).text = "Component"
    table.cell(0,1).text = "Value"
    table.cell(1,0).text = ""
    table.cell(1,1).text = ""

    doc.add_heading("3. Integration Scenarios", level=1)
    doc.add_heading("3.1 Scenario Description", level=2)
    doc.add_paragraph(
        f"The {iflow} scenario processes inbound data and delivers it to the target system."
    )

# ---------------- MAIN ----------------
for iflow in os.listdir(BASE):
    iflow_path = f"{BASE}/{iflow}"
    if not os.path.isdir(iflow_path):
        continue

    if not any(f.endswith(".iflw") for f in os.listdir(iflow_path)):
        continue

    doc = Document()
    add_header(doc)
    title_page(doc, iflow)
    toc_page(doc)
    content(doc, iflow)

    out_doc = f"{iflow_path}/{iflow}.docx"
    doc.save(out_doc)

    # Markdown (same content, clean)
    with open(f"{iflow_path}/{iflow}.md", "w") as md:
        md.write(f"""# {iflow}

## 1. Introduction
### 1.1 Purpose
Integration using SAP CPI.

### 1.2 Scope
Covers architecture and scenarios.

## 2. Integration Overview
### 2.1 Integration Architecture
Sender → CPI → Receiver

### 2.2 Integration Components
| Component | Value |
|---------|-------|
| Sender | |
| Receiver | |
""")

print("✅ Documents generated inside each iFlow folder")
