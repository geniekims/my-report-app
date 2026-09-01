import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Polygon, Line
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import datetime
import re
import math

# 1. 페이지 설정 및 UI 스타일
st.set_page_config(page_title="다차원 성향 분석 레포트", page_icon="🧭", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F1F5F9; }
    h1, h2, h3 { color: #0F172A; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white; border-radius: 6px; font-weight: 600; border: none; 
        padding: 0.7rem 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #4338CA 0%, #6D28D9 100%);
    }
    .report-box {
        background-color: white; padding: 40px; border-radius: 12px;
        box-shadow: 0 4px 6px -4px rgba(0,0,0,0.05); margin-top: 20px; border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='background: linear-gradient(135deg, #1E293B 0%, #4F46E5 100%); padding: 30px; border-radius: 12px; text-align: center; color: white; margin-bottom: 20px;'>
        <h1 style='color: white; margin-bottom: 5px; font-size: 26px;'>다차원 심층 성향 분석 레포트</h1>
        <p style='color: #CBD5E1; font-size: 14px; margin: 0;'>선천적 기질 및 9원 내면 동기 지표 종합 분석 (대량 밀도형)</p>
    </div>
""", unsafe_allow_html=True)

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.markdown("### 👤 기본 정보 입력")
    col1, col2, col3 = st.columns(3)
    with col1: name = st.text_input("성명", value="주진희")
    with col2: birth = st.date_input("생년월일", value=datetime.date(2000, 1, 1), min_value=datetime.date(1920, 1, 1))
    with col3: blood_type = st.selectbox("생체 기질 분류", ["A형", "B형", "O형", "AB형"])
    
    st.markdown("---")
    st.markdown("### 📊 9원 성향 지표 점수 입력 (각 항목별 최대 20점)")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        e1 = st.number_input("1번 (원칙/완벽)", 0, 20, 15)
        e4 = st.number_input("4번 (독창/예술)", 0, 20, 12)
        e7 = st.number_input("7번 (열정/비전)", 0, 20, 14)
    with col_e2:
        e2 = st.number_input("2번 (조력/공감)", 0, 20, 16)
        e5 = st.number_input("5번 (탐구/분석)", 0, 20, 18)
        e8 = st.number_input("8번 (도전/결단)", 0, 20, 13)
    with col_e3:
        e3 = st.number_input("3번 (성취/목표)", 0, 20, 17)
        e6 = st.number_input("6번 (책임/안정)", 0, 20, 15)
        e9 = st.number_input("9번 (조화/수용)", 0, 20, 14)

    submitted = st.form_submit_button("다차원 성향 심층 분석 레포트 생성", use_container_width=True)

def clean_markdown_text(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

# 3. 차트 생성 함수 (막대그래프 & 9각형 레이더차트)
def create_indicator_bar_chart(scores, width=265, height=220):
    labels = ["온전성", "사교성", "리더십", "적극성", "긍정성"]
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.8, rx=4, ry=4))
    d.add(String(width/2, height-22, "종합 성향 지표 (예측 점수)", fontName='NanumGothicBold', fontSize=10, fillColor=colors.HexColor('#0F172A'), textAnchor='middle'))

    bar_h = 10
    gap = (height - 60) / 5
    
    for i in range(5):
        score = scores[i]
        y_pos = height - 55 - (i * gap)
        
        d.add(String(15, y_pos + 2, labels[i], fontName='NanumGothicBold', fontSize=8, fillColor=colors.HexColor('#0F172A')))
        d.add(String(width - 35, y_pos + 2, f"{score}점", fontName='NanumGothicBold', fontSize=8, fillColor=colors.HexColor('#4F46E5')))
        
        max_bar_w = width - 90
        d.add(Rect(50, y_pos, max_bar_w, bar_h, fillColor=colors.HexColor('#E2E8F0'), strokeColor=None, rx=3, ry=3))
        bar_width = (score / 100.0) * max_bar_w
        color = '#6366F1' if i % 2 == 0 else '#3B82F6'
        d.add(Rect(50, y_pos, bar_width, bar_h, fillColor=colors.HexColor(color), strokeColor=None, rx=3, ry=3))
    return d

def create_radar_chart(scores, width=265, height=220):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.8, rx=4, ry=4))
    d.add(String(width/2, height-22, "9원 성향 지표 (9각형 분포도)", fontName='NanumGothicBold', fontSize=10, fillColor=colors.HexColor('#0F172A'), textAnchor='middle'))
    
    center_x, center_y = width/2, height/2 - 10
    max_r = 70
    
    # 배경 다각형 격자
    for level in [1, 2, 3]:
        r = max_r * (level / 3.0)
        points = []
        for i in range(9):
            angle = i * (360/9) * math.pi / 180 - math.pi/2
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            points.extend([x, y])
        d.add(Polygon(points, fillColor=None, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.5))
    
    # 축 및 라벨
    labels = ['1.원칙', '2.조력', '3.성취', '4.독창', '5.탐구', '6.책임', '7.열정', '8.도전', '9.조화']
    for i in range(9):
        angle = i * (360/9) * math.pi / 180 - math.pi/2
        x = center_x + max_r * math.cos(angle)
        y = center_y + max_r * math.sin(angle)
        d.add(Line(center_x, center_y, x, y, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.5))
        
        lx = center_x + (max_r + 14) * math.cos(angle)
        ly = center_y + (max_r + 14) * math.sin(angle) - 3
        d.add(String(lx-9, ly, labels[i], fontName='NanumGothic', fontSize=7, fillColor=colors.HexColor('#334155')))
        
    # 데이터 다각형 (9각형)
    data_points = []
    for i in range(9):
        angle = i * (360/9) * math.pi / 180 - math.pi/2
        r = max_r * (scores[i] / 20.0)
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        data_points.extend([x, y])
        
    d.add(Polygon(data_points, fillColor=colors.Color(79/255.0, 70/255.0, 229/255.0, 0.4), strokeColor=colors.HexColor('#4F46E5'), strokeWidth=1.5))
    return d

# 4. PDF 생성 함수 (대량 텍스트 & 여백 최소화 최적화)
def create_pdf(text_content, user_name, comp_scores, nine_scores):
    filename = f"{user_name}_Multidimensional_Analysis_Report.pdf"
    # 여백 최소화 (Margin 줄임)
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=20, bottomMargin=20)
    
    font_path = "NanumGothic.ttf"
    bold_path = "NanumGothicBold.ttf"
    if not os.path.exists(bold_path): bold_path = font_path
    
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_path))
    except: pass
    
    title_style = ParagraphStyle('MainTitle', fontName='NanumGothicBold', fontSize=12, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName='NanumGothicBold', fontSize=10, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName='NanumGothicBold', fontSize=8.5, textColor=colors.HexColor('#4F46E5'), spaceBefore=2, spaceAfter=2)
    # 텍스트 밀도 높임 (줄간격 타이트하게)
    body_style = ParagraphStyle('Body', fontName='NanumGothic', fontSize=8, leading=12, textColor=colors.HexColor('#334155'), spaceAfter=2)
    th_style = ParagraphStyle('TableHeader', fontName='NanumGothicBold', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#1E293B'))
    td_style = ParagraphStyle('TableData', fontName='NanumGothic', fontSize=8, leading=11.5, alignment=TA_LEFT)

    story = []
    
    # 상단 배너
    banner = Table([[Paragraph(f"<b>다차원 성향 심층 분석 레포트 &nbsp;|&nbsp; {user_name} 님</b>", title_style)]], colWidths=[545], rowHeights=[24])
    banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E293B')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(banner)
    story.append(Spacer(1, 4))
    
    # 차트 좌우 나란히 배치 (공간 절약)
    chart_table = Table([[create_indicator_bar_chart(comp_scores), create_radar_chart(nine_scores)]], colWidths=[272, 272])
    chart_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(chart_table)
    story.append(Spacer(1, 6))

    # 본문 렌더링
    table_data = []
    for line in text_content.split('\n'):
        line = line.strip()
        if not line: continue
        
        # 스코어 태그 숨김 처리
        if line.startswith('<SCORES>') or line.startswith('</SCORES>'): continue
        
        if line.startswith('|'):
            if '---' in line: continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            row_cells = [Paragraph(clean_markdown_text(col), th_style) if len(table_data) == 0 else Paragraph(clean_markdown_text(col), td_style) for col in cols]
            table_data.append(row_cells)
            continue
        
        if table_data:
            col_widths = [100, 445] if len(table_data[0]) == 2 else None
            t = Table(table_data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER' if len(table_data[0]) > 2 else 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F8FAFC')),
            ]))
            story.append(t)
            story.append(Spacer(1, 4))
            table_data = []

        if line.startswith('## '):
            sec = Table([[Paragraph(line[3:], header_style)]], colWidths=[545], rowHeights=[18])
            sec.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4F46E5')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(Spacer(1, 3))
            story.append(sec)
            story.append(Spacer(1, 2))
        elif line.startswith('### '):
            story.append(Paragraph(clean_markdown_text(line[4:]), sub_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {clean_markdown_text(line[2:])}", body_style))
        else:
            story.append(Paragraph(clean_markdown_text(line), body_style))
            
    if table_data:
        t = Table(table_data)
        t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1'))]))
        story.append(t)

    doc.build(story)
    return filename

# 5. 프롬프트 구성 및 OpenAI API 호출
if submitted:
    if not name: 
        st.warning("성명을 입력해주세요.")
    else:
        with st.spinner("🧭 다차원 데이터를 융합하여 심층 레포트를 작성 중입니다... (대량 텍스트 생성중)"):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 다차원 기질 및 조직 심리 분석 전문가
            # RULES & CONSTRAINTS:
            1. 절대 금지 사항: 특정 진단 및 분석 명칭('사주', '명리', '별자리', '혈액형', 'MBTI', '에니어그램' 등)을 출력물에 절대 직접 언급하지 말 것. 
               - 대신 '선천적 출생 기운', '출생 절기적 특성', '생체적 기질', '9원 내면 동기 지표' 등 간접적이고 전문적인 심리학/철학 용어로 반드시 대체하여 서술할 것.
            2. 성향 예측 점수(핵심): 결과물 맨 첫 줄에 반드시 다음 형식으로 5가지 종합 점수를 출력하라. (숫자는 0~100 사이)
               <SCORES>온전성:85, 사교성:72, 리더십:90, 적극성:88, 긍정성:76</SCORES>
            3. 분석 기반: 제공된 생년월일 데이터와 생체 기질, 9가지 성향 점수를 융합하여 입체적으로 분석하라.
            4. **대량 텍스트 출력### 시각화 레이아웃 변환 및 밀집 출력 스크립트

요청하신 조건에 맞춰 여백(Margin/Padding)을 최소화하고, 종합 성향 지표와 에니어그램을 한 페이지에 최대한 타일 형태로 꽉 채워 대량 렌더링하는 Python 데이터 시각화 스크립트입니다. 

**주요 적용 사항:**
*   **종합 성향 지표:** 수직 막대그래프(`Bar Chart`) 적용
*   **에니어그램 점수표:** 극좌표계(`Polar`)를 활용하여 $360^\circ / 9 = 40^\circ$ 간격의 9각형 방사형 도표(Radar Chart) 적용
*   **대량 출력:** `GridSpec` 여백 제로 세팅으로 빈 공간 완벽 제거 및 눈금표(Tick) 생략

---

```python
import matplotlib.pyplot as plt
import numpy as np

# 1. 설정 및 가상 데이터 준비 (대량 출력용)
num_records = 12 # 한 페이지에 출력할 개체 수
categories_bar = ['A', 'B', 'C', 'D', 'E']
enneagram_types = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

# 2. 여백 없는 서브플롯 그리드 설정 (6행 4열: 12명 * (막대1 + 방사형1))
# A4 비율: figsize=(8.27, 11.69)
fig, axes = plt.subplots(6, 4, figsize=(8.27, 11.69))

# 여백 및 요소 간격 최소화 (빈 공간 제거)
plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99, wspace=0.05, hspace=0.05)

for i in range(num_records):
    row = i // 2
    col_base = (i % 2) * 2
    
    # 데이터 난수 생성 (실제 데이터 맵핑 위치)
    bar_data = np.random.randint(10, 100, 5)
    enneagram_data = np.random.randint(10, 100, 9)
    
    # --- [1] 종합 성향 지표 (막대그래프) ---
    ax_bar = axes[row, col_base]
    ax_bar.bar(categories_bar, bar_data, color='#4A90E2', width=0.8)
    ax_bar.set_xticks([]) # 시각적 밀집도를 위해 축 눈금 제거
    ax_bar.set_yticks([])
    ax_bar.spines['top'].set_visible(False)
    ax_bar.spines['right'].set_visible(False)
    
    # --- [2] 에니어그램 점수표 (9각형 도표) ---
    # 기본 사각형 axes를 지우고 Polar 좌표계로 덮어쓰기
    axes[row, col_base + 1].remove()
    ax_radar = fig.add_subplot(6, 4, row * 4 + col_base + 2, polar=True)
    
    # 9각형 각도 계산 및 다각형 닫기
    angles = np.linspace(0, 2 * np.pi, 9, endpoint=False).tolist()
    enneagram_data = np.append(enneagram_data, enneagram_data[0])
    angles += angles[:1]
    
    # 도표 렌더링
    ax_radar.plot(angles, enneagram_data, color='#E24A4A', linewidth=1.2)
    ax_radar.fill(angles, enneagram_data, color='#E24A4A', alpha=0.3)
    
    # 9각형 라벨 세팅 및 불필요한 내부 원형 눈금 제거
    ax_radar.set_thetagrids(np.degrees(angles[:-1]), enneagram_types, fontsize=7)
    ax_radar.set_yticklabels([]) 
    ax_radar.spines['polar'].set_visible(False) # 외곽선 제거로 밀집도 극대화

# 대량 출력용 PDF 저장 (pad_inches=0 으로 렌더링 여백 삭감)
# plt.savefig('output_bulk.pdf', bbox_inches='tight', pad_inches=0)
plt.show()
