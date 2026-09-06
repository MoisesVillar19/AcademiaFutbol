from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import ParagraphStyle as PS
import os
from datetime import date

try:
    from utils.constants import APP_DIR
    _logo_path = os.path.join(APP_DIR, "assets", "images", "logo_roncalli.png")
except Exception:
    _logo_path = None


def exportar_a_pdf(datos: list[dict], columnas: list[tuple[str, str]], titulo: str, ruta_archivo: str) -> tuple[bool, str]:
    if not datos:
        return False, "No hay datos para exportar"
    try:
        os.makedirs(os.path.dirname(ruta_archivo) or ".", exist_ok=True)
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm, leftMargin=10*mm, rightMargin=10*mm,
                                title=titulo, author="Academia Deportiva")
        styles = getSampleStyleSheet()
        style_title = PS('Title2', parent=styles['Title'], fontSize=14, textColor=colors.HexColor('#3D1559'), alignment=TA_CENTER, spaceAfter=6)
        style_sub = PS('Sub', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#6B5B7B'), alignment=TA_CENTER)
        style_cell = PS('Cell', parent=styles['Normal'], fontSize=7, leading=9)
        style_header = PS('Header', parent=styles['Normal'], fontSize=7, textColor=colors.white, alignment=TA_CENTER)

        elems = []
        # Logo si existe
        if _logo_path and os.path.isfile(_logo_path):
            try:
                elems.append(RLImage(_logo_path, width=40*mm, height=13*mm))
            except Exception:
                pass
        elems.append(Paragraph(titulo, style_title))
        elems.append(Paragraph(f"Fecha: {date.today().strftime('%d/%m/%Y')}  •  Academia Deportiva", style_sub))
        elems.append(Spacer(1, 4*mm))

        # Tabla
        headers = [Paragraph(f"<b>{h}</b>", style_header) for _, h in columnas]
        data = [headers]
        for fila in datos:
            row = []
            for key, _ in columnas:
                val = fila.get(key, "")
                # truncar periodos largos
                txt = str(val)
                if len(txt) > 35:
                    txt = txt[:32] + "..."
                row.append(Paragraph(txt, style_cell))
            data.append(row)

        # Anchos: distribuir
        col_widths = [ (A4[0]-20*mm) / len(columnas) ] * len(columnas)
        t = Table(data, colWidths=col_widths, repeatRows=1)
        # Estilo
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F5FA')]),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ])
        # TOTAL negrita fondo claro si última fila es TOTAL
        if datos and str(datos[-1].get(columnas[0][0],"")).upper() == "TOTAL":
            style.add('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E2EFDA'))
            style.add('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
            style.add('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#1F4E78'))
        t.setStyle(style)
        elems.append(t)
        elems.append(Spacer(1, 6*mm))
        elems.append(Paragraph(f"Generado: {date.today().isoformat()} • {len(datos)} registros", style_sub))
        # Firma
        elems.append(Spacer(1, 8*mm))
        elems.append(Paragraph("___________________________<br/>Firma responsable", PS('Sign', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#6B5B7B'))))

        doc.build(elems)
        return True, f"Reporte PDF exportado: {ruta_archivo}"
    except Exception as e:
        return False, f"Error al exportar PDF: {str(e)}"
