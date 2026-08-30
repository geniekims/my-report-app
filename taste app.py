import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import re

# 1. 페이지 설정 및 UI 스타일
st.set_page_config(page_title="Executive Intelligence Report", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    h1, h2, h3 { color: #2B4C7E; font-weight: bold; }
    .stButton>button {
        background-color: #2B4C7E; color: white; border-radius: 4px;
        font-weight: 600; border: none; padding: 0.6rem 1.2rem;
    }
    .stButton>button:hover { background-color: #1F385C; }
    .report-box {
        background-color: white; padding: 30px; border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2B4C7E; background-color:#E9EEF5; padding:20px; border-radius:8px;'>심층 역량 및 직무 적합도 평가 보고서</h1>", unsafe_allow_html=True)

# 2. 사용자 입력 폼 (기존 입력 폼 유지)
with st.form("user_input_form"):
    st.markdown("### 👤 기본 프로필 및 심리 성향 진단")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: 
        name = st.text_input("성명", value="홍길동", placeholder="예: 홍길동")
    with col2: 
        birth = st.date_input(
            "생년월일", 
            value=datetime.date(2000, 1, 1), 
            min_value=datetime.date(1950, 1, 1), 
            max_value=datetime.date.today()
        )
    with col3: 
        blood_type = st.selectbox("혈액형", ["A형", "B형", "O형", "AB형"])
    
    mbti_list = [
        "ISTJ", "ISFJ", "INFJ", "INTJ", 
        "ISTP", "ISFP", "INFP", "INTP", 
        "ESTP", "ESFP", "ENFP", "ENTP", 
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]
    with col4: 
        mbti = st.selectbox("MBTI", mbti_list)
    with col5: 
        job = st.text_input("직무 / 전공", value="생산직", placeholder="예: 생산직")
    
    st.markdown("---")
    st.markdown("### 📊 다차원 내면 동기 척도 (0~20점)")
    st.caption("※ 성격 5요인 및 직무 핵심 역량 지표는 입력된 프로필과 내면 동기 척도를 기반으로 AI가 자동 유추·도출합니다.")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        e1 = st.number_input("완벽성 및 원칙 지향", 0, 20, 15)
        e4 = st.number_input("독창성 및 표현 지향", 0, 20, 12)
        e7 = st.number_input("열정 및 비전 지향", 0, 20, 10)
    with col_e2:
        e2 = st.number_input("조력 및 공감 지향", 0, 20, 14)
        e5 = st.number_input("탐구 및 분석 지향", 0, 20, 18)
        e8 = st.number_input("도전 및 결단 지향", 0, 20, 11)
    with col_e3:
        e3 = st.number_input("성취 및 목표 지향", 0, 20, 16)
        e6 = st.number_input("책임 및 안정 지향", 0, 20, 13)
        e9 = st.number_input("조화 및 수용 지향", 0, 20, 9)

    submitted = st.form_submit_button("종합 평가 보고서 생성", use_container_width=True)

# 마크다운 볼드(**) 기호를 HTML 태그로 변환하는 함수
def clean_markdown_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

# 3. TCI 스타일 가로 게이지 바 도형 생성 함수 (단어 정의 및 점수 해설 포함)
def create_tci_gauge_drawing(title, definition, score, low_desc, high_desc):
    d = Drawing(535, 65)
    d.add(Rect(0, 0, 535, 65, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#B4C6E7'), strokeWidth=0.5, rx=4, ry=4))
    
    d.add(String(12, 48, title, fontName='NanumGothicBold', fontSize=10, fillColor=colors.HexColor('#2B4C7E')))
    d.add(String(130, 49, f"[{definition}]", fontName='NanumGothic', fontSize=8.5, fillColor=colors.HexColor('#555555')))
    
    # 0~20점 척도를 100점 환산하여 등급 산출
    normalized_score = int((score / 20.0) * 100)
    grade = "M (중간)"
    badge_color = colors.HexColor('#4A70B0')
    if normalized_score <= 40:
        grade = "L (낮음)"
        badge_color = colors.HexColor('#D9534F')
    elif normalized_score >= 76:
        grade = "H (높음)"
        badge_color = colors.HexColor('#28A745')

    d.add(String(440, 48, f"환산점수: {normalized_score}점 ({grade})", fontName='NanumGothicBold', fontSize=9, fillColor=badge_color))
    
    # 게이지 바 바탕
    d.add(Rect(120, 22, 295, 10, fillColor=colors.HexColor('#E2E8F0'), strokeColor=None, rx=3, ry=3))
    bar_w = (normalized_score / 100.0) * 295
    d.add(Rect(120, 22, bar_w, 10, fillColor=badge_color, strokeColor=None, rx=3, ry=3))
    
    d.add(String(15, 8, f"낮음 특징: {low_desc}", fontName='NanumGothic', fontSize=7.5, fillColor=colors.HexColor('#666666')))
    d.add(String(415, 8, f"높음 특징: {high_desc}", fontName='NanumGothic', fontSize=7.5, fillColor=colors.HexColor('#666666')))
    
    return d

# 4. 2페이지 고정형 PDF 생성 함수
def create_pdf(text_page1, text_page2, user_name, motiv_scores):
    filename = f"{user_name}_Assessment_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=25, bottomMargin=25)
    
    font_path = "NanumGothic.ttf"
    bold_path = "NanumGothicBold.ttf"
    if not os.path.exists(bold_path): bold_path = font_path
    
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_path))
    except:
        pass
    
    title_style = ParagraphStyle('MainTitle', fontName='NanumGothicBold', fontSize=14, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName='NanumGothicBold', fontSize=10.5, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName='NanumGothicBold', fontSize=9.5, textColor=colors.HexColor('#2B4C7E'), spaceBefore=4, spaceAfter=2)
    body_style = ParagraphStyle('Body', fontName='NanumGothic', fontSize=8.5, leading=13, textColor=colors.HexColor('#333333'))
    th_style = ParagraphStyle('TableHeader', fontName='NanumGothicBold', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#1F385C'))
    td_style = ParagraphStyle('TableData', fontName='NanumGothic', fontSize=8, leading=11, alignment=TA_LEFT)

    story = []
    
    # -------------------------------------------------------------------------
    # [PAGE 1] 기질 및 성격 진단 (TCI 스타일 게이지 바 5종 + 본문 1)
    # -------------------------------------------------------------------------
    banner1 = Table([[Paragraph(f"<b>심층 역량 및 직무 적합도 통합 평가 (1/2) | {user_name}</b>", title_style)]], colWidths=[535], rowHeights=[28])
    banner1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#2B4C7E')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(banner1)
    story.append(Spacer(1, 6))
    
    # 내면 동기 지표를 활용한 TCI 스타일 가로 게이지 바 생성
    story.append(create_tci_gauge_drawing("1. 완벽성 및 원칙 지향", "규율 준수 및 세부 사항에 대한 정밀 통제 능력", motiv_scores[0], "유연하나 실수가 잦을 수 있음", "철저한 기준 준수, 정교한 업무 처리"))
    story.append(Spacer(1, 4))
    story.append(create_tci_gauge_drawing("2. 조력 및 공감 지향", "타인의 감정 수용 및 조직 내 협조 성향", motiv_scores[1], "독립적 업무 선호, 타인 무관심", "뛰어난 대인관계 공감, 화합 주도"))
    story.append(Spacer(1, 4))
    story.append(create_tci_gauge_drawing("3. 성취 및 목표 지향", "결과물 창출을 위한 높은 성취 동기와 집념", motiv_scores[2], "안정 위주, 도전 의지 부족", "강한 목표 달성력, 탁월한 추진력"))
    story.append(Spacer(1, 4))
    story.append(create_tci_gauge_drawing("4. 탐구 및 분석 지향", "원인 분석 및 지적 호기심의 깊이", motiv_scores[3], "표피적 이해에 머무름", "깊이 있는 구조 분석 및 본질 통찰"))
    story.append(Spacer(1, 4))
    story.append(create_tci_gauge_drawing("5. 열정 및 비전 지향", "미래 지향적 가치 추구 및 변화 몰입도", motiv_scores[4], "현실 안주 성향", "혁신적 아이디어 발굴, 높은 몰입도"))
    story.append(Spacer(1, 6))
    
    for line in text_page1.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('## '):
            sec = Table([[Paragraph(line[3:], header_style)]], colWidths=[535], rowHeights=[20])
            sec.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4A70B0')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(sec)
            story.append(Spacer(1, 3))
        elif line.startswith('### '):
            story.append(Paragraph(clean_markdown_text(line[4:]), sub_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {clean_markdown_text(line[2:])}", body_style))
            story.append(Spacer(1, 1))
        else:
            story.append(Paragraph(clean_markdown_text(line), body_style))
            story.append(Spacer(1, 1))

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # [PAGE 2] 심층 분석, 인문교양, 토론형 강의, 사유 고도화 및 액션 플랜
    # -------------------------------------------------------------------------
    banner2 = Table([[Paragraph(f"<b>마스터 액션 플랜 및 심층 역량 보고서 (2/2) | {user_name}</b>", title_style)]], colWidths=[535], rowHeights=[28])
    banner2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#2B4C7E')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(banner2)
    story.append(Spacer(1, 8))

    table_data = []
    for line in text_page2.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('|'):
            if '---' in line: continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            row_cells = [Paragraph(clean_markdown_text(col), th_style) if len(table_data) == 0 else Paragraph(clean_markdown_text(col), td_style) for col in cols]
            table_data.append(row_cells)
            continue
        
        if table_data:
            t = Table(table_data, colWidths=[100, 190, 245])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDE6F0')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B4C6E7')),
                ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F4F7FB')),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))
            table_data = []

        if line.startswith('## '):
            sec2 = Table([[Paragraph(line[3:], header_style)]], colWidths=[535], rowHeights=[20])
            sec2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4A70B0')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(sec2)
            story.append(Spacer(1, 3))
        elif line.startswith('### '):
            story.append(Paragraph(clean_markdown_text(line[4:]), sub_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {clean_markdown_text(line[2:])}", body_style))
            story.append(Spacer(1, 2))
        else:
            story.append(Paragraph(clean_markdown_text(line), body_style))
            story.append(Spacer(1, 2))
            
    if table_data:
        t = Table(table_data, colWidths=[100, 190, 245])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDE6F0')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B4C6E7')), ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F4F7FB'))]))
        story.append(t)

    doc.build(story)
    return filename

# 5. AI 실행 및 화면 출력
if submitted:
    if not name: 
        st.warning("성명을 입력해주세요.")
    else:
        with st.spinner("대상자의 심층 성향과 역량을 바탕으로 인문교양 학습, 토론형 강의, 생각 고도화 전략이 포함된 2페이지 풀구성 리포트를 생성 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 수석 커리어 컨설턴트 및 조직 심리 전략가
            # RULES & CONSTRAINTS:
            1. 절대 금지 사항: 결과물 내에서 '사주', '명리', '별자리', 'MBTI', '에니어그램' 등 특정 진단 방법의 명칭이나 출처를 직접적으로 언급하거나 노출하지 말 것. 오직 전문적인 심리 기질 분석 및 행동 패턴 용어만 사용할 것.
            2. 내용 풍성화: 정확히 2페이지 분량을 가득 채울 수 있도록 각 항목별로 매우 상세하고 깊이 있게 작성할 것.
            3. 마스터플랜 반영: 인문교양 학습 필요성, 토론 형식의 강의 수강을 통한 소통 및 비판적 사고 함양, 그리고 심층적인 생각의 고도화 방안을 구체적인 액션 플랜으로 반드시 포함할 것.
            4. 출력 형식: 반드시 아래의 구분자(`---PAGE_SPLIT---`)를 기준으로 페이지 1과 페이지 2 내용으로 나누어 출력할 것.
            
            # OUTPUT FORMAT:
            ## 심리 동기 및 행동 패턴 심층 분석
            - **고유 에너지 원천과 동기 구조**: (매우 상세히 기술)
            - **성격적 강점과 현업 업무 스타일**: (매우 상세히 기술)
            - **무의식적 스트레스 요인 및 대응 메커니즘**: (매우 상세히 기술)
            
            ## 직무 적합도 및 핵심 역량 정밀 진단
            - **강점 극대화 영역 및 발휘 시나리오**: (매우 상세히 기술)
            - **잠재적 리스크 관리 및 보완 전략**: (상세 기술)
            ---PAGE_SPLIT---
            ## 인문교양 학습 및 사유의 지평 확장
            - **인문교양 학습의 필요성과 실천 방안**: (상세 기술)
            - **토론 형식의 강의 수강을 통한 다원적 사고 함양**: (상세 기술)
            - **메타인지 강화를 통한 심층적 생각의 고도화**: (상세 기술)
            
            ## Master Action Plan & 전략 과제표
            | 영역 구분 | 현재 역량 및 기질 진단 | 맞춤형 성장 액션 플랜 |
            | :--- | :--- | :--- |
            | **인문교양 학습** | (진단 내용 기술) | (구체적 학습 액션 기술) |
            | **토론형 강의 몰입** | (진단 내용 기술) | (구체적 강의/토론 액션 기술) |
            | **사유 체계 고도화** | (진단 내용 기술) | (구체적 사유 고도화 액션 기술) |
            
            ## 종합 마스터플랜 실행 가이드
            - **고전 텍스트 정독 및 비판적 에세이 작성 수행**: (구체적 시나리오 제시)
            - **소크라테스식 토론 세미나 및 그룹 세션 적극 참여**: (시나리오 제시)
            """
            
            user_data = f"- 이름: {name}, 직무: {job}\n- 프로필코드: {mbti}, 생년월일: {birth}, 혈액형: {blood_type}\n- 내면동기척도: 완벽({e1}),조력({e2}),성취({e3}),독창({e4}),탐구({e5}),책임({e6}),열정({e7}),결단({e8}),조화({e9})"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                temperature=0.6, 
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_data}]
            )
            raw_content = response.choices[0].message.content.strip()
            
            if "---PAGE_SPLIT---" in raw_content:
                page1_text, page2_text = raw_content.split("---PAGE_SPLIT---")
            else:
                parts = raw_content.split("## 인문교양 학습")
                page1_text = parts[0]
                page2_text = "## 인문교양 학습" + parts[1] if len(parts) > 1 else raw_content
            
            st.success("✅ 인문교양, 토론형 강의, 심층 생각 고도화 마스터플랜이 포함된 2페이지 풀구성 리포트가 생성되었습니다.")
            
            # 웹 화면 출력
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            st.markdown("### [PAGE 1] 기질 및 심리 동기 진단 결과")
            st.markdown(page1_text)
            st.markdown("---")
            st.markdown("### [PAGE 2] 인문교양·토론 및 마스터 액션 플랜")
            st.markdown(page2_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # PDF 다운로드 버튼
            pdf_file = create_pdf(page1_text, page2_text, name, [e1, e2, e3, e4, e7])
            with open(pdf_file, "rb") as f:
                st.download_button("📕 2페이지 통합 보고서 PDF 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
