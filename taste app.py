import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import datetime
import re

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
        box-shadow: 0 6px 8px -1px rgba(0,0,0,0.15);
    }
    .report-box {
        background-color: white; padding: 40px; border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -4px rgba(0,0,0,0.05);
        margin-top: 20px; border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='background: linear-gradient(135deg, #1E293B 0%, #4F46E5 100%); padding: 30px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h1 style='color: white; margin-bottom: 10px; font-size: 28px;'>다차원 성향 분석 레포트</h1>
        <p style='color: #CBD5E1; font-size: 15px; margin: 0;'>선천적 기질 및 9원 내면 동기 지표 종합 분석 및 마스터플랜</p>
    </div>
""", unsafe_allow_html=True)

# 2. 사용자 입력 폼 (UI에서도 특정 명칭 직접 노출 최소화)
with st.form("user_input_form"):
    st.markdown("### 👤 기본 정보 입력")
    col1, col2, col3 = st.columns(3)
    with col1: 
        name = st.text_input("성명", value="주진희")
    with col2: 
        birth = st.date_input("생년월일", value=datetime.date(2000, 1, 1), min_value=datetime.date(1920, 1, 1))
    with col3: 
        blood_type = st.selectbox("생체 기질 분류", ["A형", "B형", "O형", "AB형"])
    
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

    submitted = st.form_submit_button("다차원 성향 분석 레포트 생성", use_container_width=True)

def clean_markdown_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

# 3. 20점 만점 기준 막대 그래프 도표 생성 함수
def create_score_bar_drawing(scores, start_idx=0, count=5):
    item_labels = [
        "1. 원칙 및 완벽 지향", "2. 조력 및 공감 지향", "3. 성취 및 목표 지향", 
        "4. 독창 및 예술 지향", "5. 탐구 및 분석 지향", "6. 책임 및 안정 지향", 
        "7. 열정 및 비전 지향", "8. 도전 및 결단 지향", "9. 조화 및 수용 지향"
    ]
    
    d = Drawing(535, count * 26)
    d.add(Rect(0, 0, 535, count * 26, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.8, rx=4, ry=4))
    
    for i in range(count):
        idx = start_idx + i
        if idx >= len(scores): break
        score = scores[idx]
        y_pos = (count - 1 - i) * 26 + 6
        
        level_text = "상" if score >= 16 else ("중" if score >= 10 else "하")
        color_code = '#059669' if level_text == "상" else ('#D97706' if level_text == "중" else '#DC2626')
        
        d.add(String(10, y_pos + 12, item_labels[idx], fontName='NanumGothicBold', fontSize=8, fillColor=colors.HexColor('#0F172A')))
        
        d.add(String(435, y_pos + 12, f"획득점수: {score}/20점", fontName='NanumGothicBold', fontSize=8, fillColor=colors.HexColor('#4F46E5')))
        d.add(String(505, y_pos + 12, f"[{level_text}]", fontName='NanumGothic', fontSize=7, fillColor=colors.HexColor(color_code)))
        
        d.add(Rect(120, y_pos, 300, 6, fillColor=colors.HexColor('#E2E8F0'), strokeColor=None, rx=3, ry=3))
        bar_width = (score / 20.0) * 300
        d.add(Rect(120, y_pos, bar_width, 6, fillColor=colors.HexColor('#6366F1'), strokeColor=None, rx=3, ry=3))
        
    return d

# 4. PDF 생성 함수
def create_pdf(text_page1, text_page2, user_name, scores):
    filename = f"{user_name}_Multidimensional_Analysis_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=20, bottomMargin=20)
    
    font_path = "NanumGothic.ttf"
    bold_path = "NanumGothicBold.ttf"
    if not os.path.exists(bold_path): bold_path = font_path
    
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_path))
    except:
        pass
    
    title_style = ParagraphStyle('MainTitle', fontName='NanumGothicBold', fontSize=11, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName='NanumGothicBold', fontSize=10, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName='NanumGothicBold', fontSize=8, textColor=colors.HexColor('#4F46E5'), spaceBefore=4, spaceAfter=2)
    body_style = ParagraphStyle('Body', fontName='NanumGothic', fontSize=7.5, leading=11, textColor=colors.HexColor('#334155'))
    th_style = ParagraphStyle('TableHeader', fontName='NanumGothicBold', fontSize=7.5, alignment=TA_CENTER, textColor=colors.HexColor('#1E293B'))
    td_style = ParagraphStyle('TableData', fontName='NanumGothic', fontSize=7.5, leading=10.5, alignment=TA_LEFT)

    story = []
    
    def process_text_to_story(text_content):
        local_story = []
        table_data = []
        for line in text_content.split('\n'):
            line = line.strip()
            if not line: continue
            
            if line.startswith('|'):
                if '---' in line: continue
                cols = [c.strip() for c in line.split('|')[1:-1]]
                row_cells = [Paragraph(clean_markdown_text(col), th_style) if len(table_data) == 0 else Paragraph(clean_markdown_text(col), td_style) for col in cols]
                table_data.append(row_cells)
                continue
            
            if table_data:
                col_widths = [100, 435] if len(table_data[0]) == 2 else None
                t = Table(table_data, colWidths=col_widths)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER' if len(table_data[0]) > 2 else 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F8FAFC')),
                ]))
                local_story.append(t)
                local_story.append(Spacer(1, 6))
                table_data = []

            if line.startswith('## '):
                sec = Table([[Paragraph(line[3:], header_style)]], colWidths=[535], rowHeights=[16])
                sec.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4F46E5')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                local_story.append(sec)
                local_story.append(Spacer(1, 4))
            elif line.startswith('### '):
                local_story.append(Paragraph(clean_markdown_text(line[4:]), sub_style))
            elif line.startswith('- '):
                local_story.append(Paragraph(f"• {clean_markdown_text(line[2:])}", body_style))
                local_story.append(Spacer(1, 2))
            else:
                local_story.append(Paragraph(clean_markdown_text(line), body_style))
                local_story.append(Spacer(1, 3))
        if table_data:
            t = Table(table_data)
            t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1'))]))
            local_story.append(t)
        return local_story

    # [PAGE 1]
    banner1 = Table([[Paragraph(f"<b>다차원 성향 분석 레포트 (1/2) &nbsp;|&nbsp; {user_name} 님</b>", title_style)]], colWidths=[535], rowHeights=[22])
    banner1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E293B')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(banner1)
    story.append(Spacer(1, 6))
    
    story.append(create_score_bar_drawing(scores, start_idx=0, count=5))
    story.append(Spacer(1, 6))
    story.extend(process_text_to_story(text_page1))
    story.append(PageBreak())

    # [PAGE 2]
    banner2 = Table([[Paragraph(f"<b>다차원 성향 분석 레포트 (2/2) &nbsp;|&nbsp; {user_name} 님</b>", title_style)]], colWidths=[535], rowHeights=[22])
    banner2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E293B')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(banner2)
    story.append(Spacer(1, 6))

    story.append(create_score_bar_drawing(scores, start_idx=5, count=4))
    story.append(Spacer(1, 6))
    story.extend(process_text_to_story(text_page2))

    doc.build(story)
    return filename

# 5. 프롬프트 구성 및 OpenAI API 호출
if submitted:
    if not name: 
        st.warning("성명을 입력해주세요.")
    else:
        with st.spinner("🧭 다차원 데이터를 융합하여 심층 레포트를 작성 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 다차원 기질 및 조직 심리 분석 전문가
            # RULES & CONSTRAINTS:
            1. 절대 금지 사항: 특정 진단 및 분석 명칭('사주', '명리', '별자리', '혈액형', 'MBTI', '에니어그램' 등)을 출력물에 절대 직접 언급하지 말 것. 
               - 대신 '선천적 출생 기운', '출생 절기적 특성', '생체적 기질', '9원 내면 동기 지표' 등 간접적이고 전문적인 심리학/철학 용어로 반드시 대체하여 서술할 것.
            2. 분석 기반: 제공된 생년월일 데이터와 생체 기질, 9가지 성향 점수를 융합하여 입체적으로 분석하되, 앞서 명시한 금지 단어들을 완벽히 배제할 것.
            3. 성향 예측 점수: 온전성, 사교성, 리더십, 적극성, 긍정성의 5가지 지표를 0~100점 사이로 도출하여 서두에 배치하라.
            4. 서술 방식: 각 섹션(1~4번)은 개조식(Bullet point)으로 핵심을 요약한 뒤, 각 기질적 요소들이 어떻게 결합되어 나타나는지 구체적이고 깊이 있는 서술형 문장(최소 4~5줄)으로 덧붙일 것.
            5. 마스터 플랜: 최종 계획표에는 [실질적 추천 3가지], [인문학 교양 추천], [모니터링 수행 및 멘토링 가이드], [새로운 한계 도전 과제]가 누락 없이 포함되어야 한다.
            6. 출력 형식: 분량을 조절하여 반드시 `---PAGE_SPLIT---`를 기준으로 1페이지와 2페이지를 나누어 출력하라.

            # OUTPUT FORMAT:
            ## 📊 종합 성향 예측 지표
            - **온전성**: [XX]점 / **사교성**: [XX]점 / **리더십**: [XX]점 / **적극성**: [XX]점 / **긍정성**: [XX]점

            ## 1. 심리 동기 및 행동 패턴 심층 분석
            - [핵심 요약 포인트 1]
            - [핵심 요약 포인트 2]
            (출생 기반의 선천적 기운, 절기적 특성, 체액적 기질, 9원 내면 동기가 융합된 상세 서술형 문장 작성 - 특정 명칭 언급 불가)

            ## 2. 직무 적합도 및 핵심 역량 정밀 진단
            - [핵심 요약 포인트 1]
            - [핵심 요약 포인트 2]
            (종합된 성향을 바탕으로 가장 높은 성과를 낼 수 있는 직무 환경과 역량 발휘 시나리오 상세 서술)

            ---PAGE_SPLIT---

            ## 3. 역량 다각화 및 사고력 향상 전략
            - [핵심 요약 포인트 1]
            - [핵심 요약 포인트 2]
            (현 상태를 넘어서기 위한 다차원적 사고력 향상 및 역량 확장 방법론 상세 서술)

            ## 4. 강점·약점 종합 및 개선 방향
            - [핵심 요약 포인트 1]
            - [핵심 요약 포인트 2]
            (선천적 강점을 극대화하고 후천적 약점을 보완하는 실질적 방향 제시)

            ## 🎯 마스터 플랜 (Action Guide)
            | 구분 | 세부 실행 과제 및 지침 |
            | :--- | :--- |
            | **실질적 추천 1** | (행동 중심의 실질적 과제 제시) |
            | **실질적 추천 2** | (행동 중심의 실질적 과제 제시) |
            | **실질적 추천 3** | (행동 중심의 실질적 과제 제시) |
            | **인문학 교양** | (사고 확장을 위한 통섭적 인문학 접근법 또는 도서 추천) |
            | **모니터링 & 멘토링** | (정기적 실행 모니터링 체계와 멘토 확보 방안) |
            | **새로운 도전** | (안전지대를 벗어나기 위한 도전 목표 제시) |
            """
            
            user_data = f"""
            - 이름: {name}, 생년월일: {birth}, 생체 기질: {blood_type}
            - 9원 성향 지표 (20점 만점): 
              1번({e1}), 2번({e2}), 3번({e3}), 4번({e4}), 5번({e5}), 
              6번({e6}), 7번({e7}), 8번({e8}), 9번({e9})
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                temperature=0.7, 
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_data}]
            )
            raw_content = response.choices[0].message.content.strip()
            
            if "---PAGE_SPLIT---" in raw_content:
                page1_text, page2_text = raw_content.split("---PAGE_SPLIT---")
            else:
                parts = raw_content.split("## 3. 역량")
                page1_text = parts[0]
                page2_text = "## 3. 역량" + parts[1] if len(parts) > 1 else raw_content
            
            st.success("🧭 다차원 성향 분석 레포트가 완성되었습니다.")
            
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            st.markdown("### [PAGE 1] 종합 성향 지표 및 심층 분석")
            st.markdown(page1_text)
            st.markdown("---")
            st.markdown("### [PAGE 2] 역량 다각화 및 마스터 플랜")
            st.markdown(page2_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
            pdf_file = create_pdf(page1_text, page2_text, name, [e1, e2, e3, e4, e5, e6, e7, e8, e9])
            with open(pdf_file, "rb") as f:
                st.download_button("📕 다차원 분석 PDF 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
