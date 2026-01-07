import sys, requests, os, json, base64
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_numbered_heading(doc, text, level, num_str):
    p = doc.add_heading(level=level)
    run = p.add_run(f"{num_str} {text}")
    run.font.color.rgb = RGBColor(31, 56, 100)
    run.font.size = Pt(16) if level == 1 else Pt(13)

def build_docx(iflow_name, author, date, ai_data, output_path):
    doc = Document()
    
    # --- HEADER LOGOS ---
    section = doc.sections[0]
    header = section.header
    htable = header.add_table(1, 2, width=Inches(6.5))
    sap_url = "https://raw.githubusercontent.com/Akila710/CPI_Demo1/main/assets/logos/SAP.jpg"
    mm_url = "https://raw.githubusercontent.com/Akila710/CPI_Demo1/main/assets/logos/mm_logo.png"
    try:
        # Use /tmp/ to keep workspace clean
        with open("/tmp/sap.jpg", "wb") as f: f.write(requests.get(sap_url).content)
        with open("/tmp/mm.png", "wb") as f: f.write(requests.get(mm_url).content)
        htable.rows[0].cells[0].paragraphs[0].add_run().add_picture("/tmp/sap.jpg", height=Inches(0.6))
        mm_p = htable.rows[0].cells[1].paragraphs[0]
        mm_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        mm_p.add_run().add_picture("/tmp/mm.png", height=Inches(0.6))
    except: pass

    # --- COVER PAGE ---
    for _ in range(5): doc.add_paragraph()
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(iflow_name)
    run.font.size = Pt(28); run.font.bold = True; run.font.color.rgb = RGBColor(31, 56, 100)
    doc.add_paragraph("Technical Specification Document").alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    meta = doc.add_table(rows=3, cols=2)
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER; meta.style = 'Table Grid'
    for i, (l, v) in enumerate([("Author:", author), ("Date:", date), ("Version:", "1.0")]):
        meta.rows[i].cells[0].text = l; meta.rows[i].cells[1].text = v
    doc.add_page_break()

    # --- CONTENT GENERATION ---
    add_numbered_heading(doc, "Introduction", 1, "1.")
    add_numbered_heading(doc, "Purpose", 2, "1.1")
    doc.add_paragraph(str(ai_data.get("purpose", "")))
    
    add_numbered_heading(doc, "Integration Overview", 1, "2.")
    add_numbered_heading(doc, "Integration Architecture", 2, "2.1")
    
    mermaid_code = ai_data.get("mermaid_diagram", "graph LR; Sender-->CPI; CPI-->Receiver;")
    graph_url = f"https://mermaid.ink/img/{base64.b64encode(mermaid_code.encode()).decode()}"
    try:
        # Save architecture diagram to /tmp/
        with open("/tmp/diagram.png", "wb") as f: f.write(requests.get(graph_url).content)
        doc.add_picture("/tmp/diagram.png", width=Inches(3.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    except: pass

    add_numbered_heading(doc, "Integration Components", 2, "2.2")
    comp_data = ai_data.get("components", {})
    c_table = doc.add_table(rows=0, cols=2)
    c_table.style = 'Table Grid'
    for key in ["Sender", "Sender Adapter", "Receiver", "Receiver Adapter"]:
        row = c_table.add_row().cells
        row[0].text = key
        row[0].paragraphs[0].runs[0].bold = True
        row[1].text = str(comp_data.get(key, "N/A"))

    add_numbered_heading(doc, "Data Flows", 2, "3.2")
    map_list = ai_data.get("mapping", [])
    if map_list:
        m_table = doc.add_table(rows=1, cols=3)
        m_table.style = 'Table Grid'
        hdr = m_table.rows[0].cells
        hdr[0].text = 'Source Field'; hdr[1].text = 'Target Field'; hdr[2].text = 'Logic'
        for m in map_list:
            row = m_table.add_row().cells
            row[0].text = str(m.get("source", "")); row[1].text = str(m.get("target", "")); row[2].text = str(m.get("logic", ""))

    doc.save(output_path)

if __name__ == "__main__":
    build_docx(sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4]), sys.argv[5])
