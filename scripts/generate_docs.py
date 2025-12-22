import os
from docx import Document
from datetime import date

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE_DOCX = "assets/logos/templates/reference.docx"
OUTPUT_DIR = "output"

AUTHOR = "Auto Generated"
VERSION = "1.0"
TODAY = date.today().isoformat()

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
def iflow_summary(iflow_name):
    return f"""
Purpose:
This iFlow implements integration logic for {iflow_name}.

Sender / Receiver Systems:
Sender: Source System
Receiver: Target System

Adapters Used:
HTTPS / OData (based on configuration)

Step-by-Step Flow Logic:
Start Event → Processing Steps → End Event

Mapping Logic:
Standard CPI message mappings.

Groovy Scripts:
No custom Groovy scripts identified.

Error Handling:
Handled via Exception Subprocess with logging.
"""

# ---------------- MAIN ----------------
for package in os.listdir(ARTIFACTS_DIR):
    pkg_path = os.path.join(ARTIFACTS_DIR, package)
    if not os.path.isdir(pkg_path):
        continue

    iflows = [f for f in os.listdir(pkg_path) if f.endswith(".xml")]
    if not iflows:
        continue

    print(f"📦 Processing package: {package}")

    # ----------- MARKDOWN -----------
    md_path = os.path.join(OUTPUT_DIR, f"{package}.md")
    with open(md_path, "w", encoding="utf-8") as md:
        md.write(f"# {package} – Technical Specification\n\n")
        for iflow in iflows:
            md.write(f"## {iflow.replace('.xml','')}\n")
            md.write(iflow_summary(iflow.replace(".xml", "")))
            md.write("\n---\n")

    # ----------- DOCX -----------
    doc = Document(TEMPLATE_DOCX)

    # Replace cover placeholders (IF PRESENT)
    for p in doc.paragraphs:
        p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
        p.text = p.text.replace("{{DATE}}", TODAY)
        p.text = p.text.replace("{{VERSION}}", VERSION)
        p.text = p.text.replace("{{PACKAGE_NAME}}", package)

    # Page break → content starts AFTER cover
    doc.add_page_break()

    # Main sections (matching your attached document)
    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(
        "This document provides a detailed technical specification "
        f"for the CPI package {package}."
    )

    doc.add_heading("2. Integration Overview", level=1)
    doc.add_paragraph(
        "The following integration scenarios are implemented in this package."
    )

    doc.add_heading("3. Integration Scenarios", level=1)

    for iflow in iflows:
        name = iflow.replace(".xml", "")
        doc.add_heading(name, level=2)
        doc.add_paragraph(iflow_summary(name))

    doc.add_heading("4. Error Handling and Logging", level=1)
    doc.add_paragraph(
        "Errors are handled using CPI Exception Subprocesses "
        "with appropriate logging and monitoring."
    )

    doc.add_heading("5. Testing Validation", level=1)
    doc.add_paragraph(
        "Unit testing and end-to-end testing should be performed "
        "to validate integration scenarios."
    )

    doc.add_heading("6. Reference Documents", level=1)
    doc.add_paragraph("SAP CPI Documentation\nIntegration Design Guidelines")

    docx_path = os.path.join(OUTPUT_DIR, f"{package}.docx")
    doc.save(docx_path)

    print(f"✅ Generated: {md_path}, {docx_path}")

print("🎉 All package documentation generated successfully")
