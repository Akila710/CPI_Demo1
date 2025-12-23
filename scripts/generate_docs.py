import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import date

PACKAGE = os.getenv("PACKAGE_NAME")
BASE_DIR = "cpi-artifacts"

SAP_LOGO = "assets/logos/SAP.jpg"
MM_LOGO = "assets/logos/mm_logo.png"

AUTHOR = ""
VERSION = "Draft"
TODAY = date.today().isoformat()

if not PACKAGE:
    raise Exception("PACKAGE_NAME not provided")

PACKAGE_PATH = os.path.join(BASE_DIR, PACKAGE)
if not os.path.isdir(PACKAGE_PATH):
    raise Exception(f"Package not found: {PACKAGE_PATH}")

# --------- helpers ---------

def add_header(doc):
    section = doc.sections[0]
    header = section.header
    header.paragraphs.clear()

    table = header.add_table(rows=1, cols=2, width=Inches(6))
    left, right = table.rows[0].cells

    left_p = left.paragraphs[0]
    left_p.add_run().add_picture(SAP_LOGO, width=Inches(1.2))
    left_p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    right_p = right.paragraphs[0]
    right_p.add_run().add_picture(MM_LOGO, width=Inches(1.4))
    right_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def title_page(doc, iflow):
    add_header(doc)

    doc.add_paragraph("\n\n\n")
    p = doc.add_paragraph(iflow)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.size = Pt(22)
    p.runs[0].bold = True

    doc.add_paragraph("\n")

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    table.cell(0,0).text = "Author"
    table.cell(0,1).text = AUTHOR
    table.cell(1,0).text = "Date"
    table.cell(1,1).text = TODAY
    table.cell(2,0).text = "Version"
    table.cell(2,1).text = VERSION

    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()


def toc_page(doc):
    add_header(doc)
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

    for t in toc:
        doc.add_paragraph(t)

    doc.add_page_break()


def body_content(doc, iflow):
    add_header(doc)

    doc.add_heading("1. Introduction", level=1)
    doc.add_heading("1.1 Purpose", level=2)
    doc.add_paragraph(f"The purpose of {iflow} is to enable integration between source and target systems using SAP CPI.")

    doc.add_heading("1.2 Scope", level=2)
    doc.add_paragraph(f"The scope includes message processing, transformation, and communication for {iflow}.")

    doc.add_heading("2. Integration Overview", level=1)

    doc.add_heading("2.1 Integration Architecture", level=2)
    doc.add_paragraph("The integration architecture consists of sender, SAP CPI runtime, and receiver systems.")

    doc.add_heading("2.2 Integration Components", level=2)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = "Component"
    table.rows[0].cells[1].text = "Value"

    components = [
        ("Sender", ""),
        ("Sender Adapter", ""),
        ("Receiver", ""),
        ("Receiver Adapter", "")
    ]

    for c, v in components:
        row = table.add_row().cells
        row[0].text = c
        row[1].text = v

    doc.add_heading("3. Integration Scenarios", level=1)
    doc.add_heading("3.1 Scenario Description", level=2)
    doc.add_paragraph(f"{iflow} processes business messages between connected systems.")

    doc.add_heading("4. Error Handling and Logging", level=1)
    doc.add_paragraph("Errors are handled using exception subprocesses and message logs.")

    doc.add_heading("5. Testing Validation", level=1)
    doc.add_paragraph("Unit and integration testing must be performed.")

    doc.add_heading("6. Reference Documents", level=1)
    doc.add_paragraph("SAP CPI Documentation.")


# --------- main ---------

for iflow in os.listdir(PACKAGE_PATH):
    iflow_path = os.path.join(PACKAGE_PATH, iflow)
    if not os.path.isdir(iflow_path):
        continue

    print(f"Processing iFlow: {iflow}")

    # markdown
    md_path = os.path.join(iflow_path, f"{iflow}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {iflow}\n\n")
        f.write("## 1. Introduction\n")
        f.write("### 1.1 Purpose\n")
        f.write(f"The purpose of {iflow} is to enable integration.\n")

    # docx
    doc = Document()
    title_page(doc, iflow)
    toc_page(doc)
    body_content(doc, iflow)

    doc.save(os.path.join(iflow_path, f"{iflow}.docx"))

print("✅ Documents generated inside iFlow folders")
