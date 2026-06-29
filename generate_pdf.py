#!/usr/bin/env python3
"""生成TCL产品PDF手册 - 支持中文"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

def find_chinese_font():
    """查找系统中可用的中文字体"""
    font_paths = [
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STSong.ttc",
        "/System/Library/Fonts/STKaiti.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None

def register_fonts():
    """注册字体"""
    chinese_font = find_chinese_font()
    if chinese_font:
        pdfmetrics.registerFont(TTFont('Chinese', chinese_font))
        print(f"使用中文字体: {chinese_font}")
        return True
    print("未找到中文字体，将使用默认字体")
    return False

def generate_pdf():
    """生成PDF产品手册"""
    register_fonts()
    
    output_path = "/Users/chenkai/Downloads/AGENT_DEMO/data/docs/tcl_product_manual.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           leftMargin=50, rightMargin=50,
                           topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    try:
        styles['Title'].fontName = 'Chinese'
        styles['Heading1'].fontName = 'Chinese'
        styles['Heading2'].fontName = 'Chinese'
        styles['Heading3'].fontName = 'Chinese'
        styles['BodyText'].fontName = 'Chinese'
        styles['Normal'].fontName = 'Chinese'
    except:
        pass
    
    styles['Title'].fontSize = 24
    styles['Title'].alignment = TA_CENTER
    styles['Heading1'].fontSize = 18
    styles['Heading1'].textColor = colors.darkblue
    styles['Heading2'].fontSize = 14
    styles['Heading2'].textColor = colors.blue
    styles['BodyText'].fontSize = 11
    styles['BodyText'].leading = 18
    
    story = []
    
    story.append(Paragraph('TCL QD-Mini LED 产品手册', styles['Title']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph('一、产品概述', styles['Heading1']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        'TCL QD-Mini LED系列电视采用量子点技术与Mini LED背光相结合，'
        '实现了精准的分区控光和广色域显示，为用户带来极致的视觉体验。',
        styles['BodyText']
    ))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph('二、核心技术特点', styles['Heading1']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph('2.1 QD-Mini LED背光技术', styles['Heading2']))
    story.append(Paragraph(
        'QD-Mini LED将Mini LED背光与量子点技术完美结合，'
        '每个LED灯珠尺寸仅为传统LED的1/100，配合量子点广色域技术，'
        '实现百万级精细控光和157% BT.709广色域覆盖。',
        styles['BodyText']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph('2.2 万象分区控光', styles['Heading2']))
    story.append(Paragraph(
        '万象分区控光技术实现了对每个背光分区的独立控制，'
        'Q10L Pro系列最高支持6042个万象分区，'
        '能够精准调节画面亮度，呈现层次分明的精彩画面。',
        styles['BodyText']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph('2.3 蝶翼华曜屏', styles['Heading2']))
    story.append(Paragraph(
        '采用纳米级仿生科技，在液晶分子上增加聚酰亚胺，'
        '有效提升对比度的同时去除画面光晕及环境光干扰，'
        '呈现更加清晰的惊艳画质。',
        styles['BodyText']
    ))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph('三、产品参数表', styles['Heading1']))
    story.append(Spacer(1, 10))
    
    data = [
        ['型号', '尺寸', '分区数量', '峰值亮度', '色域', '刷新率'],
        ['Q10L Pro', '98英寸', '6042', '2000nits', '157% BT.709', '120Hz'],
        ['Q10L Pro', '85英寸', '5184', '2000nits', '157% BT.709', '120Hz'],
        ['X11L', '98英寸', '20736', '10000nits', '100% BT.2020', '120Hz'],
        ['T7H', '85英寸', '330', '1300nits', '96% DCI-P3', '144Hz'],
        ['T7H', '75英寸', '220', '1100nits', '96% DCI-P3', '144Hz'],
    ]
    
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Chinese'),
        ('FONTNAME', (0, 1), (-1, -1), 'Chinese'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table = Table(data, colWidths=[80, 80, 80, 90, 100, 70])
    table.setStyle(table_style)
    story.append(table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph('四、产品系列介绍', styles['Heading1']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph('4.1 Q10L Pro系列', styles['Heading2']))
    story.append(Paragraph(
        'Q10L Pro是TCL第四代液晶电视代表作，采用蝶翼华曜屏和极景·无黑边100%全面屏设计，'
        '配备6042个万象分区控光，带来极致视觉体验。',
        styles['BodyText']
    ))
    story.append(ListFlowable([
        ListItem(Paragraph('蝶翼华曜屏 屏中贵族 超旗舰', styles['BodyText'])),
        ListItem(Paragraph('极景·无黑边 100%全面屏', styles['BodyText'])),
        ListItem(Paragraph('6042个万象分区 远超12000级普通分区控光效果', styles['BodyText'])),
    ], bulletType='1'))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph('4.2 X11L系列', styles['Heading2']))
    story.append(Paragraph(
        'X11L是TCL旗舰级QD-Mini LED电视，拥有20736个万象分区和10000nits峰值亮度，'
        '100% BT.2020全局高色域，代表行业顶级水平。',
        styles['BodyText']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph('4.3 T7H系列', styles['Heading2']))
    story.append(Paragraph(
        'T7H高画质真HDR电视，330分区精细控光，HDR 1300nits峰值亮度，'
        '96% DCI-P3电影级原色高色域，全通道4K 144Hz，是高性价比之选。',
        styles['BodyText']
    ))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph('五、适用场景', styles['Heading1']))
    story.append(Spacer(1, 10))
    story.append(ListFlowable([
        ListItem(Paragraph('家庭影院：QD-Mini LED技术带来影院级观影体验', styles['BodyText'])),
        ListItem(Paragraph('游戏娱乐：120Hz/144Hz高刷新率，HDMI 2.1接口', styles['BodyText'])),
        ListItem(Paragraph('客厅观影：超大屏幕带来沉浸式体验', styles['BodyText'])),
        ListItem(Paragraph('高端会议室：旗舰级画质适合商务展示', styles['BodyText'])),
    ], bulletType='1'))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph('六、服务与支持', styles['Heading1']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        'TCL提供全国联保服务，整机保修1年，主要部件保修3年。'
        '如需安装可致电TCL全国统一服务热线4008123456预约当地工程师上门安装调试。',
        styles['BodyText']
    ))
    
    doc.build(story)
    print(f"\nPDF文件已成功生成: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path) / 1024:.2f} KB")

if __name__ == "__main__":
    print("=" * 60)
    print("TCL产品PDF手册生成器")
    print("=" * 60)
    generate_pdf()
    print("\n" + "=" * 60)
    print("生成完成！")
    print("=" * 60)