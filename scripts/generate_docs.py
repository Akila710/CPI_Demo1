import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

BASE_DIR = "cpi-artifacts"
PACKAGE = os.getenv("PACKAGE_NAME")
TODAY = date.today().isoformat()
VERSION = "Draft"

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

if not PACKAGE:
    raise Exception("PACKAGE_NAME not provided")

pkg_path = os.path.join(BASE_DIR, PACKAGE)
if not os.path.isdir(pkg_path):
    raise Exception(f"Package not found: {pkg_path}")

iflows = [d for d in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, d))]
if not iflows:
    raise Exception("No iFlows found")

# --------------------------------------------------
def add_header(doc):
    section = doc.sections[0]
    header = section.header

    if header.paragraphs and header.paragraphs[0].text.strip():
        return  # header already exists

    table = header.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(3)
    table.columns[1].width = Inches(3)

    left = table.cell(0, 0).paragraphs[0]
    left.add_run().add_picture(SAP_LOGO, width=Inches(1.2))
    left.alignment = WD_ALIGN_PARAGRAPH.LEFT

    right = table.cell(0, 1).paragraphs[0]
    right.add_run().add_picture(MM_LOGO, width=Inches(1.4))
    right.alignment = WD_ALIGN_PARAGRAPH.RIGHT

# --------------------------------------------------
def title_page(doc, iflow):
    p = doc.add_paragraph(iflow)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.size = Pt(20)
    p.runs[0].bold = True

    doc.add_paragraph("")

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Author"
    table.cell(1, 0).text = "Date"
    table.cell(2, 0).text = "Version"

    table.cell(0, 1).text = ""
    table.cell(1, 1).text = TODAY
    table.cell(2, 1).text = VERSION

    doc.add_page_break()

# --------------------------------------------------
def toc_page(doc):
    h = doc.add_paragraph("Table of Contents")
    h.runs[0].bold = True
    h.runs[0].font.size = Pt(14)

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

# --------------------------------------------------
def content_pages(doc, iflow):
    doc.add_heading("1. Introduction", level=1)
    doc.add_heading("1.1 Purpose", level=2)
    doc.add_paragraph(
        f"The purpose of {iflow} is to integrate data between sender and receiver systems."
    )

    doc.add_heading("1.2 Scope", level=2)
    doc.add_paragraph(
        "This document describes architecture, components, and integration behavior."
    )

    doc.add_heading("2. Integration Overview", level=1)
    doc.add_heading("2.1 Integration Architecture", level=2)
    doc.add_paragraph(
        "The integration architecture includes sender, SAP CPI, and receiver systems."
    )

    doc.add_heading("2.2 Integration Components", level=2)

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Component"
    table.cell(0, 1).text = "Value"

    table.add_row().cells[0].text = "Sender"
    table.rows[1].cells[1].text = "External System"

    table.add_row().cells[0].text = "Sender Adapter"
    table.rows[2].cells[1].text = "HTTPS"

    table.add_row().cells[0].text = "Receiver"
    table.rows[3].cells[1].text = "SAP S/4HANA"

    table.add_row().cells[0].text = "Receiver Adapter"
    table.rows[4].cells[1].text = "ODATA"

    doc.add_heading("3. Integration Scenarios", level=1)
    doc.add_heading("3.1 Scenario Description", level=2)
    doc.add_paragraph(
        f"The {iflow} scenario processes inbound messages and delivers them to target systems."
    )

# --------------------------------------------------
for iflow in iflows:
    doc = Document()
    add_header(doc)
    title_page(doc, iflow)
    toc_page(doc)
    content_pages(doc, iflow)

    out = os.path.join(pkg_path, iflow, f"{iflow}.docx")
    doc.save(out)

    with open(os.path.join(pkg_path, iflow, f"{iflow}.md"), "w") as f:
        f.write(f"# {iflow}\n\nGenerated documentation.")

print("✅ Documents generated successfully")
