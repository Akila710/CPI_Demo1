import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

PACKAGE = os.getenv("PACKAGE_NAME")
BASE_DIR = f"cpi-artifacts/{PACKAGE}"

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

TODAY = date.today().isoformat()
VERSION = "Draft"

if not os.path.isdir(BASE_DIR):
    raise Exception(f"Package not found: {BASE_DIR}")

# ---------------- HEADER (ONCE) ----------------
def add_header(doc):
    section = doc.sections[0]
    header = section.header
    header.paragraphs.clear()

    table = header.add_table(rows=1, cols=2, width=section.page_width)
    left, right = table.rows[0].cells

    lp = left.paragraphs[0]
    lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    lp.add_run().add_picture(SAP_LOGO, width=Inches(1.2))

    rp = right.paragraphs[0]
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rp.add_run().add_picture(MM_LOGO, width=Inches(1.2))

# ---------------- TITLE PAGE ----------------
def add_title_page(doc, iflow):
    p = doc.add_paragraph(iflow)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.size = Pt(24)
    p.runs[0].bold = True

    doc.add_paragraph("")

    table = doc.add_table(rows=3, cols=2)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table.cell(0,0).text = "Author"
    table.cell(0,1).text = ""
    table.cell(1,0).text = "Date"
    table.cell(1,1).text = TODAY
    table.cell(2,0).text = "Version"
    table.cell(2,1).text = VERSION

    doc.add_page_break()

# ---------------- TOC PAGE ----------------
def add_toc(doc):
    doc.add_heading("Table of Contents", level=1)

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
def add_content(doc, iflow):
    doc.add_heading("1. Introduction", level=1)
    doc.add_heading("1.1 Purpose", level=2)
    doc.add_paragraph(
        f"The purpose of {iflow} is to integrate source and target systems "
        "using SAP Cloud Platform Integration."
    )

    doc.add_heading("1.2 Scope", level=2)
    doc.add_paragraph(
        f"This document covers the design, architecture, and execution of {iflow}."
    )

    doc.add_heading("2. Integration Overview", level=1)
    doc.add_heading("2.1 Integration Architecture", level=2)
    doc.add_paragraph("The integration architecture is illustrated below.")

    doc.add_heading("2.2 Integration Components", level=2)

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.cell(0,0).text = "Component"
    table.cell(0,1).text = "Value"

    rows = [
        ("Sender", "Source System"),
        ("Sender Adapter", "HTTPS"),
        ("Receiver", "Target System"),
        ("Receiver Adapter", "ODATA")
    ]

    for r in rows:
        c = table.add_row().cells
        c[0].text = r[0]
        c[1].text = r[1]

    doc.add_heading("3. Integration Scenarios", level=1)
    doc.add_heading("3.1 Scenario Description", level=2)
    doc.add_paragraph(
        f"The {iflow} scenario involves message processing, transformation, "
        "and delivery between systems."
    )

    doc.add_heading("4. Error Handling and Logging", level=1)
    doc.add_paragraph("Errors are handled using CPI exception subprocesses.")

    doc.add_heading("5. Testing Validation", level=1)
    doc.add_paragraph("Functional and integration testing is performed.")

    doc.add_heading("6. Reference Documents", level=1)
    doc.add_paragraph("SAP CPI Documentation")

# ---------------- MAIN ----------------
for iflow in os.listdir(BASE_DIR):
    IFLOW_PATH = os.path.join(BASE_DIR, iflow)
    if not os.path.isdir(IFLOW_PATH):
        continue

    doc = Document()
    add_header(doc)
    add_title_page(doc, iflow)
    add_toc(doc)
    add_content(doc, iflow)

    doc_path = os.path.join(IFLOW_PATH, f"{iflow}.docx")
    md_path = os.path.join(IFLOW_PATH, f"{iflow}.md")

    doc.save(doc_path)

    with open(md_path, "w") as md:
        md.write(f"# {iflow}\n\n")
        md.write("## 1. Introduction\n")
        md.write("### 1.1 Purpose\n")
        md.write(f"{iflow} integration purpose.\n")

    print(f"✅ Generated docs for {iflow}")
