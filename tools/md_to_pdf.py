import re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Preformatted, ListFlowable, ListItem
from reportlab.lib import colors

SRC = r"D:\Hp\Desktop\AcademiaFutbol\docs\despliegue\instalacion.md"
DST = r"D:\Hp\Desktop\AcademiaFutbol\docs\despliegue\instalacion.pdf"

COLORS = {
    "primary": HexColor("#1B3A5C"),
    "accent": HexColor("#2E86C1"),
    "gray": HexColor("#5D6D7E"),
    "light": HexColor("#EAF2F8"),
    "code_bg": HexColor("#F4F6F7"),
    "warn": HexColor("#F39C12"),
    "success": HexColor("#27AE60"),
}

styles = getSampleStyleSheet()
sTitle = ParagraphStyle("Title2", parent=styles["Title"], fontSize=22, textColor=COLORS["primary"], spaceAfter=4*mm, alignment=TA_CENTER, fontName="Helvetica-Bold")
sSub = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9, textColor=COLORS["gray"], alignment=TA_CENTER, spaceAfter=6*mm, fontName="Helvetica-Oblique")
sH1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, textColor=COLORS["primary"], spaceBefore=8*mm, spaceAfter=3*mm, fontName="Helvetica-Bold", keepWithNext=True)
sH2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11, textColor=COLORS["primary"], spaceBefore=6*mm, spaceAfter=2*mm, fontName="Helvetica-Bold", keepWithNext=True, borderPadding=(2,0,2,6), backColor=COLORS["light"])
sH3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=10, textColor=HexColor("#2C3E50"), spaceBefore=4*mm, spaceAfter=2*mm, fontName="Helvetica-Bold")
sBody = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=13, alignment=TA_JUSTIFY, spaceAfter=2*mm, fontName="Helvetica", textColor=HexColor("#2C3E50"))
sBullet = ParagraphStyle("Bullet", parent=sBody, leftIndent=12, bulletIndent=6, spaceAfter=1.5*mm)
sCode = ParagraphStyle("Code", parent=styles["Code"], fontSize=7.5, leading=10, fontName="Courier", textColor=HexColor("#1A1A1A"), backColor=COLORS["code_bg"], borderPadding=(4,4,4,5), spaceAfter=3*mm)
sCodeInline = ParagraphStyle("CodeInline", parent=sBody, fontName="Courier", fontSize=8, textColor=HexColor("#7D3C98"))
sTableCell = ParagraphStyle("TC", parent=styles["Normal"], fontSize=7.5, leading=10, fontName="Helvetica", textColor=HexColor("#2C3E50"))
sTableHeader = ParagraphStyle("TH", parent=sTableCell, fontName="Helvetica-Bold", textColor=white, alignment=TA_CENTER)
sCaption = ParagraphStyle("Caption", parent=styles["Normal"], fontSize=7, textColor=COLORS["gray"], alignment=TA_CENTER, fontName="Helvetica-Oblique")

def parse_md(text):
    lines = text.splitlines()
    blocks = []
    i=0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            blocks.append(("h1", line[2:].strip()))
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
        elif line.startswith("#### "):
            blocks.append(("h3", line[5:].strip()))
        elif line.strip().startswith("> "):
            blocks.append(("quote", line.strip()[2:].strip()))
            # join multi-line quotes
            j=i+1
            extra=[]
            while j<len(lines) and lines[j].strip().startswith(">"):
                extra.append(lines[j].strip()[1:].strip())
                j+=1
            if extra:
                blocks[-1]=("quote", blocks[-1][1]+" ".join(extra))
                i=j-1
        elif line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            j=i+1
            code=[]
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j+=1
            blocks.append(("code", "\n".join(code), lang))
            i=j
        elif line.strip().startswith("|") and "|" in line:
            # table
            rows=[]
            j=i
            while j < len(lines) and lines[j].strip().startswith("|"):
                # skip separator row with ---
                if re.match(r"^\|\s*[-|:\s]+\|\s*$", lines[j]):
                    j+=1
                    continue
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                rows.append(cells)
                j+=1
            if rows:
                blocks.append(("table", rows))
            i=j-1
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            items=[]
            j=i
            while j < len(lines) and (lines[j].strip().startswith("- ") or lines[j].strip().startswith("* ") or (lines[j].startswith("  ") and items)):
                if lines[j].strip().startswith("- ") or lines[j].strip().startswith("* "):
                    items.append(lines[j].strip()[2:].strip())
                elif lines[j].strip():
                    items[-1] += " " + lines[j].strip()
                j+=1
            blocks.append(("ul", items))
            i=j-1
        elif re.match(r"^\d+\.\s", line.strip()):
            items=[]
            j=i
            while j < len(lines) and re.match(r"^\d+\.\s", lines[j].strip()):
                items.append(re.sub(r"^\d+\.\s", "", lines[j].strip()))
                # continuation indented lines
                k=j+1
                while k < len(lines) and lines[k].startswith("   ") and lines[k].strip() and not re.match(r"^\d+\.\s", lines[k].strip()) and not lines[k].strip().startswith("-"):
                    items[-1] += " " + lines[k].strip()
                    k+=1
                j=k
            blocks.append(("ol", items))
            i=j-1
        elif line.strip() == "---":
            blocks.append(("hr", None))
        elif line.strip() == "":
            pass
        else:
            # paragraph: collect until blank or block
            para=[line.strip()]
            j=i+1
            while j < len(lines) and lines[j].strip()!="" and not lines[j].startswith("#") and not lines[j].strip().startswith("```") and not lines[j].strip().startswith("|") and not lines[j].strip().startswith("- ") and not re.match(r"^\d+\.\s", lines[j].strip()) and not lines[j].strip().startswith(">"):
                para.append(lines[j].strip())
                j+=1
            blocks.append(("p", " ".join(para)))
            i=j-1
        i+=1
    return blocks

def md_inline(text):
    # sanitize unicode no soportado por Helvetica
    text = text.replace("\u2192", "->").replace("\u2014", "-").replace("\u2013", "-").replace("\u2714", "OK").replace("\u2705", "[OK]").replace("\u274c", "[X]").replace("\u2192", "->")
    # escape for reportlab
    # handle `code` -> <font face="Courier" color="#7D3C98">code</font>
    # handle **bold** -> <b>
    # handle *italic* -> <i>
    # handle [text](url) -> text (url)
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # links
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'\1 (\2)', t)
    # inline code
    t = re.sub(r"`([^`]+)`", r'<font face="Courier" color="#7D3C98">\1</font>', t)
    # bold
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"__([^_]+)__", r"<b>\1</b>", t)
    # italic single * (avoid already bold)
    # keep simple
    return t

def build_pdf():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    blocks = parse_md(text)

    doc = SimpleDocTemplate(DST, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=15*mm, bottomMargin=15*mm, title="Guía de Instalación — AcademiaFutbol v1.0.0", author="Academia Deportiva")
    
    story=[]
    # Header
    # Extract first h1 as title
    title_found=False
    for idx, b in enumerate(blocks):
        if b[0]=="h1" and not title_found:
            story.append(Paragraph(md_inline(b[1]), sTitle))
            title_found=True
            continue
        if b[0]=="quote" and idx<3:
            story.append(Paragraph(md_inline(b[1]), sSub))
            story.append(HRFlowable(width="60%", thickness=0.5, color=COLORS["accent"], spaceAfter=4*mm, spaceBefore=2*mm, hAlign="CENTER"))
            continue
        if b[0]=="h1":
            story.append(Paragraph(md_inline(b[1]), sH1))
        elif b[0]=="h2":
            story.append(Paragraph(md_inline(b[1]), sH2))
        elif b[0]=="h3":
            story.append(Paragraph(md_inline(b[1]), sH3))
        elif b[0]=="quote":
            style = ParagraphStyle("Quote", parent=sBody, leftIndent=8, borderPadding=(6,6,6,8), backColor=HexColor("#FEF9E7"), borderColor=COLORS["warn"], borderWidth=1, textColor=HexColor("#7D6608"), fontName="Helvetica-Oblique", fontSize=8)
            story.append(Paragraph(md_inline(b[1]), style))
            story.append(Spacer(1,2*mm))
        elif b[0]=="p":
            story.append(Paragraph(md_inline(b[1]), sBody))
        elif b[0]=="code":
            code_text = b[1]
            # Preformatted keeps whitespace
            pf = Preformatted(code_text, sCode, maxLineLength=95)
            # wrap in table for bg
            t = Table([[pf]], colWidths=[doc.width])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), COLORS["code_bg"]),
                ("BOX", (0,0), (-1,-1), 0.4, HexColor("#BDC3C7")),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("RIGHTPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1,1*mm))
        elif b[0]=="ul":
            lst=[]
            for it in b[1]:
                lst.append(Paragraph(md_inline(it), sBullet))
            # render as list with bullets
            for p in lst:
                story.append(Table([["•", p]], colWidths=[8, doc.width-8], style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),1),("RIGHTPADDING",(0,0),(-1,-1),1)])))
                story[-1].setStyle(TableStyle([]))
            story.append(Spacer(1,1*mm))
        elif b[0]=="ol":
            for idx2, it in enumerate(b[1], start=1):
                p = Paragraph(md_inline(it), sBullet)
                story.append(Table([[f"{idx2}.", p]], colWidths=[10, doc.width-10], style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),1)])))
            story.append(Spacer(1,1*mm))
        elif b[0]=="table":
            rows = b[1]
            # create paragraphs for cells
            hdr = rows[0]
            data=[]
            # header row
            hdr_cells=[Paragraph(md_inline(c), sTableHeader) for c in hdr]
            data.append(hdr_cells)
            for r in rows[1:]:
                # pad if missing
                while len(r) < len(hdr):
                    r.append("")
                data.append([Paragraph(md_inline(c), sTableCell) for c in r])
            # col widths proportional
            ncols=len(hdr)
            available = doc.width
            # guess widths: if 3 cols give equal, if 2 cols 30%/70%
            if ncols==2:
                cw=[available*0.28, available*0.72]
            elif ncols==3:
                cw=[available*0.22, available*0.38, available*0.40]
            elif ncols==4:
                cw=[available/ncols]*ncols
            else:
                cw=[available/ncols]*ncols
            t=Table(data, colWidths=cw, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), COLORS["primary"]),
                ("TEXTCOLOR", (0,0), (-1,0), white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,0), 7.5),
                ("ALIGN", (0,0), (-1,0), "CENTER"),
                ("BACKGROUND", (0,1), (-1,-1), white),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#F8F9F9")]),
                ("GRID", (0,0), (-1,-1), 0.4, HexColor("#AEB6BF")),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0), (-1,-1), 4),
                ("RIGHTPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ]))
            story.append(t)
            story.append(Spacer(1,3*mm))
        elif b[0]=="hr":
            story.append(HRFlowable(width="100%", thickness=0.4, color=HexColor("#D5D8DC"), spaceAfter=3*mm, spaceBefore=3*mm))
    
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(COLORS["gray"])
        canvas.drawString(18*mm, 12*mm, "AcademiaFutbol v1.0.0 — Guía de Instalación — BD OneDrive virgen")
        canvas.drawRightString(A4[0]-18*mm, 12*mm, f"Página {doc.page}")
        # line
        canvas.setStrokeColor(COLORS["accent"])
        canvas.setLineWidth(0.6)
        canvas.line(18*mm, 14*mm, A4[0]-18*mm, 14*mm)
        canvas.restoreState()
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF generado: {DST} ({os.path.getsize(DST)} bytes)")

if __name__=="__main__":
    build_pdf()
