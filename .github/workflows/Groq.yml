import os
from docx import Document
from datetime import date
import sys

# ---------------- CONFIG ----------------
ARTIFACTS_DIR = "cpi-artifacts"
TEMPLATE_DOCX = "assets/logos/templates/reference.docx"
OUTPUT_DIR = "output"

AUTHOR = "Auto Generated"
VERSION = "1.0"
TODAY = date.today().isoformat()

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
def iflow_summary_block(iflow_name):
    return f"""
Purpose:
This iFlow implements integration logic for {iflow_name}.

Sender / Receiver Systems:
Sender: Source System
Receiver: Target System

Adapters Used:
HTTPS / OData (based on configuration)

Step-by-Step Flow Logic:
Start Event → Processing → End Event

Mapping Logic:
Standard CPI message mapping is applied.

Groovy Scripts:
No custom Groovy scripts used.

Error Handling:
Handled via Exception Subprocess with logging.
"""

# ---------------- USER INPUT ----------------
package_name = input("Enter CPI package name: ").strip()

package_path = os.path.join(ARTIFACTS_DIR, package_name)

if not os.path.isdir(package_path):
    print(f"❌ Package '{package_name}' not found in {ARTIFACTS_DIR}")
    sys.exit(1)

iflows = [f for f in os.listdir(package_path) if f.endswith(".xml")]

if not iflows:
    print(f"❌ No iFlows found inside package '{package_name}'")
    sys.exit(1)

print(f"📦 Package: {package_name}")
print(f"🔎 Found iFlows: {', '.join(iflows)}")

# ---------------- MARKDOWN ----------------
md_path = os.path.join(OUTPUT_DIR, f"{package_name}.md")

with open(md_path, "w", encoding="utf-8") as md:
    md.write(f"# {package_name} – Technical Specification\n\n")

    for iflow in iflows:
        name = iflow.replace(".xml", "")
        md.write(f"## {name}\n")
        md.write(iflow_summary_block(name))
        md.write("\n---\n")

print(f"✅ Markdown generated: {md_path}")

# ---------------- DOCX ----------------
doc = Document(TEMPLATE_DOCX)

# Replace placeholders on COVER PAGE (if present)
for p in doc.paragraphs:
    p.text = p.text.replace("{{AUTHOR}}", AUTHOR)
    p.text = p.text.replace("{{DATE}}", TODAY)
    p.text = p.text.replace("{{VERSION}}", VERSION)
    p.text = p.text.replace("{{PACKAGE_NAME}}", package_name)

# Page break → start content after cover
doc.add_page_break()

# ---- DOCUMENT STRUCTURE (MATCHES YOUR DOC) ----
doc.add_heading("1. Introduction", level=1)
doc.add_paragraph(
    "This document provides a detailed technical specification "
    f"for the SAP CPI package '{package_name}'."
)

doc.add_heading("1.1 Purpose", level=2)
doc.add_paragraph(
    "The purpose of this document is to describe the integration "
    "scenarios implemented using SAP Cloud Platform Integration."
)

doc.add_heading("1.2 Scope", level=2)
doc.add_paragraph(
    "This document covers iFlow design, integration logic, "
    "error handling, and testing considerations."
)

doc.add_heading("2. Integration Overview", level=1)
doc.add_paragraph(
    "This package contains the following integration flows:"
)

doc.add_heading("3. Integration Scenarios", level=1)

for iflow in iflows:
    name = iflow.replace(".xml", "")
    doc.add_heading(name, level=2)
    doc.add_paragraph(iflow_summary_block(name))

doc.add_heading("4. Error Handling and Logging", level=1)
doc.add_paragraph(
    "Error handling is implemented using CPI Exception Subprocesses "
    "with message logging and monitoring."
)

doc.add_heading("5. Testing Validation", level=1)
doc.add_paragraph(
    "Unit testing and end-to-end testing should be conducted "
    "for all integration scenarios."
)

doc.add_heading("6. Reference Documents", level=1)
doc.add_paragraph(
    "SAP CPI Documentation\nIntegration Design Guidelines"
)

docx_path = os.path.join(OUTPUT_DIR, f"{package_name}.docx")
doc.save(docx_path)

print(f"✅ DOCX generated: {docx_path}")
print("🎉 Documentation generation completed successfully")
