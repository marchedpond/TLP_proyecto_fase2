#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar PDF académico del proyecto TLP Fase 2
Convierte el README.md a un PDF con formato académico similar al PDF de Fase 1
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, Flowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
import re
import os


def parse_markdown_to_elements(markdown_text):
    """Convierte texto markdown a elementos de ReportLab"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#000000'),
        spaceAfter=12,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#000000'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#000000'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        spaceBefore=8,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#000000'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        textColor=colors.HexColor('#000000'),
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        backColor=colors.HexColor('#F5F5F5')
    )
    
    lines = markdown_text.split('\n')
    in_code_block = False
    code_block_lines = []
    table_lines = []
    in_table = False
    pending_title = None  # Para agrupar título con tabla
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Manejar bloques de código
        if line.strip().startswith('```'):
            if in_code_block:
                # Cerrar bloque de código
                if code_block_lines:
                    code_text = '\n'.join(code_block_lines)
                    elements.append(Paragraph(f'<font face="Courier" size="9">{escape_html(code_text)}</font>', code_style))
                    elements.append(Spacer(1, 6))
                code_block_lines = []
                in_code_block = False
            else:
                # Cerrar tabla si estaba abierta
                if in_table:
                    table = parse_table('\n'.join(table_lines))
                    if table:
                        # Si hay un título pendiente, agruparlo con la tabla
                        if pending_title:
                            elements.append(KeepTogether([pending_title, Spacer(1, 4), table]))
                            pending_title = None
                        else:
                            elements.append(KeepTogether(table))
                        elements.append(Spacer(1, 12))
                    table_lines = []
                    in_table = False
                # Abrir bloque de código
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue
        
        # Detectar tablas (línea que contiene |)
        if '|' in line and not line.strip().startswith('#'):
            if not in_table:
                in_table = True
            table_lines.append(line)
            i += 1
            continue
        else:
            # Si estábamos en una tabla, procesarla
            if in_table:
                table = parse_table('\n'.join(table_lines))
                if table:
                    # Si hay un título pendiente, agruparlo con la tabla usando KeepTogether
                    if pending_title:
                        # Crear grupo con título y tabla para mantenerlos juntos
                        group = KeepTogether([
                            pending_title,
                            Spacer(1, 4),
                            table
                        ])
                        elements.append(group)
                        pending_title = None
                    else:
                        elements.append(KeepTogether(table))
                    elements.append(Spacer(1, 12))
                table_lines = []
                in_table = False
        
        # Saltar líneas vacías
        if not line.strip():
            # Si hay un título pendiente y viene una línea vacía, podría ser antes de una tabla
            # Verificar si la siguiente línea no vacía es una tabla
            if pending_title and i + 1 < len(lines):
                next_non_empty = None
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        next_non_empty = lines[j].strip()
                        break
                # Si la siguiente línea es una tabla, no agregar el título aún
                if next_non_empty and '|' in next_non_empty:
                    i += 1
                    continue
            
            if elements and not isinstance(elements[-1], Spacer) and not pending_title:
                elements.append(Spacer(1, 6))
            i += 1
            continue
        
        # Encabezados
        if line.startswith('# '):
            text = line[2:].strip()
            # Saltar el título principal "Informe Fase 2" ya que se agrega manualmente
            if 'Informe Fase 2' in text:
                i += 1
                continue
            # Verificar si la siguiente línea no vacía es una tabla
            next_is_table = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                if '|' in next_line and not next_line.startswith('#'):
                    next_is_table = True
                break
            
            title_para = Paragraph(escape_html(text), title_style)
            if next_is_table:
                pending_title = title_para
            else:
                elements.append(title_para)
                elements.append(Spacer(1, 12))
        elif line.startswith('## '):
            text = line[3:].strip()
            # Verificar si la siguiente línea no vacía es una tabla
            next_is_table = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                if '|' in next_line and not next_line.startswith('#'):
                    next_is_table = True
                break
            
            title_para = Paragraph(escape_html(text), heading1_style)
            if next_is_table:
                pending_title = title_para
            else:
                elements.append(title_para)
                elements.append(Spacer(1, 8))
        elif line.startswith('### '):
            text = line[4:].strip()
            # Verificar si la siguiente línea no vacía es una tabla
            next_is_table = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                if '|' in next_line and not next_line.startswith('#'):
                    next_is_table = True
                break
            
            title_para = Paragraph(escape_html(text), heading2_style)
            if next_is_table:
                pending_title = title_para
            else:
                elements.append(title_para)
                elements.append(Spacer(1, 6))
        elif line.startswith('#### '):
            text = line[5:].strip()
            # Verificar si la siguiente línea no vacía es una tabla
            next_is_table = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                if '|' in next_line and not next_line.startswith('#'):
                    next_is_table = True
                break
            
            title_para = Paragraph(escape_html(text), heading3_style)
            if next_is_table:
                pending_title = title_para
            else:
                elements.append(title_para)
                elements.append(Spacer(1, 4))
        # Listas
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            # Si hay título pendiente, agregarlo primero
            if pending_title:
                elements.append(pending_title)
                elements.append(Spacer(1, 6))
                pending_title = None
            text = line.strip()[2:].strip()
            para_text = f'• {process_markdown_inline(text)}'
            elements.append(Paragraph(para_text, normal_style))
            elements.append(Spacer(1, 4))
        # Líneas horizontales
        elif line.strip() == '---':
            # Si hay título pendiente, agregarlo primero
            if pending_title:
                elements.append(pending_title)
                elements.append(Spacer(1, 6))
                pending_title = None
            elements.append(Spacer(1, 12))
        # Texto normal
        else:
            # Si hay título pendiente, agregarlo primero
            if pending_title:
                elements.append(pending_title)
                elements.append(Spacer(1, 6))
                pending_title = None
            para_text = process_markdown_inline(line)
            if para_text.strip():
                elements.append(Paragraph(para_text, normal_style))
                elements.append(Spacer(1, 6))
        
        i += 1
    
    # Procesar tabla al final si quedó abierta
    if in_table and table_lines:
        table = parse_table('\n'.join(table_lines))
        if table:
            # Si hay un título pendiente, agruparlo con la tabla usando KeepTogether
            if pending_title:
                # Crear grupo con título y tabla para mantenerlos juntos
                group = KeepTogether([
                    pending_title,
                    Spacer(1, 4),
                    table
                ])
                elements.append(group)
                pending_title = None
            else:
                elements.append(KeepTogether(table))
            elements.append(Spacer(1, 12))
    
    # Si queda un título pendiente sin tabla, agregarlo
    if pending_title:
        elements.append(pending_title)
        elements.append(Spacer(1, 8))
    
    return elements

def process_markdown_inline(text):
    """Procesa elementos inline de markdown como bold, italic, code"""
    text = escape_html(text)
    
    # Negrita **texto** o __texto__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Cursiva *texto* o _texto_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    
    # Código inline `código`
    text = re.sub(r'`(.+?)`', r'<font face="Courier" size="9">\1</font>', text)
    
    return text

def escape_html(text):
    """Escapa caracteres HTML especiales"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def parse_table(text):
    """Parsea una tabla markdown a formato Table de ReportLab"""
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if not lines:
        return None
    
    # Separar filas de datos y encabezados
    header_cells = []
    data_rows = []
    is_header = True
    
    for line in lines:
        # Separar por |
        cells = [cell.strip() for cell in line.split('|')]
        # Quitar celdas vacías del principio y final
        cells = [c for c in cells if c]
        # Filtrar líneas separadoras (solo contienen - o :)
        if not cells or all(ch in '-: ' for ch in ''.join(cells)):
            if is_header and header_cells:
                is_header = False
            continue
        
        # Procesar celdas
        processed_cells = []
        for cell in cells:
            processed_cells.append(cell)
        
        if is_header:
            header_cells = processed_cells
            is_header = False
        else:
            data_rows.append(processed_cells)
    
    if not header_cells:
        return None
    
    num_cols = len(header_cells)
    
    # Crear estilo para encabezados
    header_style = ParagraphStyle(
        'TableHeader',
        fontSize=10,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        textColor=colors.HexColor('#000000'),
        spaceBefore=0,
        spaceAfter=0
    )
    
    # Crear estilo para celdas de datos
    cell_style = ParagraphStyle(
        'TableCell',
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_LEFT,
        textColor=colors.HexColor('#000000'),
        spaceBefore=0,
        spaceAfter=0
    )
    
    # Crear encabezados en negrita
    header_paragraphs = []
    for cell_text in header_cells:
        processed_text = process_markdown_inline(cell_text)
        header_paragraphs.append(Paragraph(f'<b>{processed_text}</b>', header_style))
    
    # Crear filas de datos
    table_data = [header_paragraphs]
    for row in data_rows:
        row_paragraphs = []
        for i, cell_text in enumerate(row):
            if i < num_cols:
                processed_text = process_markdown_inline(cell_text)
                row_paragraphs.append(Paragraph(processed_text, cell_style))
            else:
                row_paragraphs.append(Paragraph('', cell_style))
        # Asegurar que todas las filas tengan el mismo número de columnas
        while len(row_paragraphs) < num_cols:
            row_paragraphs.append(Paragraph('', cell_style))
        table_data.append(row_paragraphs)
    
    # Calcular ancho de columnas de manera más inteligente
    # Ancho total disponible: 7.5 pulgadas (8.5 - 2 márgenes de 0.5)
    total_width = 7.5 * inch
    if num_cols == 2:
        col_widths = [4.5*inch, 3.0*inch]
    elif num_cols == 3:
        col_widths = [2.8*inch, 2.5*inch, 2.2*inch]
    elif num_cols == 4:
        col_widths = [2.0*inch, 2.0*inch, 2.0*inch, 1.5*inch]
    elif num_cols == 5:
        col_widths = [1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]
    else:
        col_width = total_width / num_cols
        col_widths = [col_width] * num_cols
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D0D0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#808080')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#000000')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F8F8')]),
    ]))
    
    return table

def generate_pdf():
    """Genera el PDF académico del proyecto"""
    
    # Leer el README.md
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Separar la parte del informe (después del separador ---)
    parts = readme_content.split('---')
    intro_content = parts[0] if len(parts) > 0 else ''
    # Tomar todo después del primer separador ---
    if len(parts) > 1:
        informe_content = '\n'.join(parts[1:])
    else:
        # Si no hay separador, usar todo el contenido desde la línea que dice "Informe Fase 2"
        lines = readme_content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if 'Informe Fase 2' in line:
                start_idx = i + 1  # Saltar la línea del título
                break
        informe_content = '\n'.join(lines[start_idx:])
    
    # Eliminar el título "Informe Fase 2" del contenido si está al inicio
    informe_lines = informe_content.split('\n')
    # Buscar y eliminar el título principal (línea que empiece con # y contenga "Informe Fase 2")
    if informe_lines:
        for i, line in enumerate(informe_lines):
            # Si la línea es un título (# ) y contiene "Informe Fase 2"
            stripped_line = line.strip()
            if stripped_line.startswith('# ') and 'Informe Fase 2' in stripped_line:
                # Eliminar esta línea y las líneas vacías siguientes
                informe_lines = informe_lines[i+1:]
                # Eliminar líneas vacías después del título
                while informe_lines and not informe_lines[0].strip():
                    informe_lines = informe_lines[1:]
                break
    informe_content = '\n'.join(informe_lines)
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        "Proyecto Fase 2.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Lista de elementos para el PDF
    story = []
    styles = getSampleStyleSheet()
    
    # ========== PORTADA ==========
    # Logo de la UCA
    logo_path = 'logo_uca.jpg'
    if os.path.exists(logo_path):
        try:
            # Leer imagen y redimensionar
            img = PILImage.open(logo_path)
            # Calcular dimensiones manteniendo aspecto (más pequeño para que quepa todo)
            max_width = 1.2 * inch
            max_height = 1.5 * inch
            width_ratio = max_width / img.width
            height_ratio = max_height / img.height
            ratio = min(width_ratio, height_ratio)
            
            new_width = img.width * ratio
            new_height = img.height * ratio
            
            logo = Image(logo_path, width=new_width, height=new_height)
            story.append(Spacer(1, 1.2*inch))
            story.append(logo)
            story.append(Spacer(1, 0.3*inch))
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el logo: {e}")
            story.append(Spacer(1, 1.5*inch))
    else:
        story.append(Spacer(1, 1.5*inch))
    
    # Título de la universidad
    title_style = ParagraphStyle(
        'UniversityTitle',
        parent=styles['Heading1'],
        fontSize=15,
        textColor=colors.HexColor('#000000'),
        spaceAfter=15,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    story.append(Paragraph('Universidad Centroamericana José Simeón Cañas', title_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Nombre del curso
    course_style = ParagraphStyle(
        'CourseStyle',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#000000'),
        spaceAfter=8,
        fontName='Helvetica',
        alignment=TA_CENTER
    )
    
    story.append(Paragraph('Teoría de lenguajes de programación<br/>Catedrático: Jaime Clímaco', course_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Tema del proyecto
    theme_style = ParagraphStyle(
        'ThemeStyle',
        parent=styles['Heading1'],
        fontSize=13,
        textColor=colors.HexColor('#000000'),
        spaceAfter=20,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )
    
    story.append(Paragraph('Mini-parser para Lenguaje Natural Limitado', theme_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Integrantes - Usar KeepTogether para evitar que se parta
    integrantes_data = [
        ['Integrante', 'Carné'],
        ['Andres Felipe Cardona Duarte', '00037820'],
        ['Axel Jared Hernández Servellón', '00145319'],
        ['Moises Ezequiel Juárez Mejía', '00038221'],
        ['Josue Alfredo Mejia Urias', '00000921'],
    ]
    
    integrantes_table = Table(integrantes_data, colWidths=[4*inch, 1.5*inch])
    integrantes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D0D0D0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFFFFF')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#808080')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#000000')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F8F8')]),
    ]))
    
    # Envolver la tabla en KeepTogether para evitar que se parta
    story.append(KeepTogether(integrantes_table))
    story.append(PageBreak())
    
    # ========== SEGUNDA PÁGINA - TÍTULO DEL INFORME ==========
    # Título del proyecto en la segunda página
    project_title_style = ParagraphStyle(
        'ProjectTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#000000'),
        spaceAfter=20,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    story.append(Paragraph('Informe Fase 2 - Mini-parser para Lenguaje Natural Limitado', project_title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # ========== CONTENIDO DEL INFORME ==========
    # Procesar el contenido del informe
    elements = parse_markdown_to_elements(informe_content)
    story.extend(elements)
    
    # Construir el PDF
    doc.build(story)
    print("PDF generado exitosamente: Proyecto Fase 2.pdf")

if __name__ == '__main__':
    generate_pdf()

