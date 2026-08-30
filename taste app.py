import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import re

# 1. 페이지 설정 및 UI 스타일 (파란색 테마 적용)
st.set_page_config(page_title="Humanities & Critical Thinking Report", page_icon="📚", layout="wide")

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

st.markdown("<h1 style='text-align: center; color: #2B4C7E; background-color:#E9EEF5; padding:20px; border-radius:8px;'>인문교양 학습 및 심층 사고 고도화 컨설팅 보고서</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555555; font-size: 15px;'>본 컨설팅은 <b>인문교양 학습, 토론 형식의 강의 수강, 그리고 심층적인 생각의 고도화</b>를 핵심 목표로 하여 개인의 성찰과 지적 성장을 지원합니다.</p>", unsafe_allow_html=True)

# 2. 사용자 입력 폼 (기본 예시: 홍길동)
with st.form("user_input_form"):
    st.markdown("### 👤 학습자 기본 프로필 및 성향 진단")
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
        job = st.text_input("관심 분야 / 전공", value="인문학 및 철학", placeholder="예: 인문학 및 철학")
    
    st.markdown("---")
    st.markdown("### 📊 인문학적 사유 및 심층 동기 척도 (0~20점)")
    st.caption("※ 본 척도는 인문교양 학습 태도, 토론 몰입도, 비판적 사고력을 진단하기 위한 지표입니다.")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        e1 = st.number_input("개념의 본질 탐구 지향", 0, 20, 16)
        e4 = st.number_input("비판적 독창성 지향", 0, 20, 13)
        e7 = st.number_input("철학적 열정 지향", 0, 20, 15)
    with col_e2:
        e2 = st.number_input("타인 관점 수용 및 공감", 0, 20, 14)
        e5 = st.number_input("텍스트 심층 분석 지향", 0, 20, 17)
        e8 = st.number_input("토론 참여 결단력", 0, 20, 12)
    with col_e3:
        e3 = st.number_input("통찰적 성취 지향", 0, 20, 15)
        e6 = st.number_input("사유의 지속성 및 책임", 0, 20, 14)
        e9 = st.number_input("다원적 조화 지향", 0, 20, 13)

    submitted = st.form_submit_button("인문교양 및 심층 사고 컨설팅 리포트 생성", use_container_width=True)

# 마크다운 볼드(**) 기호를 깔끔한 HTML 태그로 변환하는 함수
def clean_markdown_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

# 3. ReportLab 자체 도형 생성 함수 (파란색 테마 적용)
def create_bar_drawing(title, categories, scores, max_val=100):
    d = Drawing(250, 145)
    d.add(Rect(0, 0, 250, 145, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#B4C6E7'), strokeWidth=0.5, rx=5, ry=5))
    d.add(String(15, 126, title, fontName='NanumGothicBold', fontSize=10, fillColor=colors.HexColor('#2B4C7E')))
    
    y = 103
    for cat, score in zip(categories, scores):
        d.add(String(15, y, cat, fontName='NanumGothic', fontSize=8, fillColor=colors.HexColor('#333333')))
        d.add(Rect(75, y+1, 120, 8, fillColor=colors.HexColor('#E2E8F0'), strokeColor=None))
        bar_width = (score / max_val) * 120
        bar_color = colors.HexColor('#2B4C7E') if score >= 60 else colors.HexColor('#D9534F')
        if max_val == 20: bar_color = colors.HexColor('#2B4C7E')
        d.add(Rect(75, y+1, bar_width, 8, fillColor=bar_color, strokeColor=None))
        d.add(String(200, y, f"{score}", fontName='NanumGothicBold', fontSize=8, fillColor=colors.HexColor('#333333')))
        y -= 20
    return d

# 4. PDF 생성 함수 (파란색 배너 및 디자인 반영)
def create_pdf(text, user_name, motiv_scores, big5_scores, sw_scores):
    filename = f"{user_name}_Humanities_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=25, bottomMargin=25)
    
    font_path = "NanumGothic.ttf"
    bold_path = "NanumGothicBold.ttf"
    if not os.path.exists(bold_path): bold_path = font_path
    
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_path))
    except:
        pass
    
    title_style = ParagraphStyle('MainTitle', fontName='NanumGothicBold', fontSize=15, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName='NanumGothicBold', fontSize=11, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName='NanumGothicBold', fontSize=10, textColor=colors.HexColor('#2B4C7E'), spaceBefore=6, spaceAfter=2)
    body_style = ParagraphStyle('Body', fontName='NanumGothic', fontSize=9, leading=14, textColor=colors.HexColor('#333333'))
    th_style = ParagraphStyle('TableHeader', fontName='NanumGothicBold', fontSize=8.5, alignment=TA_CENTER, textColor=colors.HexColor('#1F385C'))
    td_style = ParagraphStyle('TableData', fontName='NanumGothic', fontSize=8.5, leading=12, alignment=TA_LEFT)

    story = []
    
    # 상단 메인 배너 (파란색 계열)
    main_banner = Table([[Paragraph(f"<b>인문교양 학습 및 심층 사고 고도화 컨설팅 | {user_name}</b>", title_style)]], colWidths=[535], rowHeights=[32])
    main_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#2B4C7E')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(main_banner)
    story.append(Spacer(1, 8))
    
    d1 = create_bar_drawing("사유 및 동기 밸런스 (0~20)", ['본질탐구·공감·성취', '독창·심층분석·책임', '열정·토론결단·조화'], [sum(motiv_scores[:3])//3, sum(motiv_scores[3:6])//3, sum(motiv_scores[6:])//3], 20)
    d2 = create_bar_drawing("인지 성향 지표 (T-Score)", ['개방성', '성실성', '외향성', '호감성', '정서안정성'], big5_scores, 100)
    d3 = create_bar_drawing("인문 학습 역량 (Blue:우수)", ['비판적독해력', '토론설득력', '다원적공감력', '철학적통찰력', '사유고도화력'], sw_scores, 100)
    
    comment_p = Paragraph("<b>[지표 분석 종합 코멘트]</b><br/><br/>본 리포트는 학습자의 인문교양 소양 함양, <b>토론 형식 강의</b>를 통한 상호작용 능력, 그리고 표피적 지식을 넘어선 <b>심층적 생각의 고도화</b> 과정을 지원하기 위해 설계되었습니다.", body_style)
    
    chart_table = Table([
        [d1, d2],
        [d3, comment_p]
    ], colWidths=[267.5, 267.5])
    chart_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('BOTTOMPADDING', (0,0), (-1,-1), 5), ('TOPPADDING', (0,0), (-1,-1), 0)]))
    story.append(chart_table)
    story.append(Spacer(1, 5))

    table_data = []
    for line in text.split('\n'):
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
                ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F4F7FB')),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
            table_data = []

        if line.startswith('## '):
            story.append(Spacer(1, 5))
            sec_banner = Table([[Paragraph(line[3:], header_style)]], colWidths=[535], rowHeights=[22])
            sec_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4A70B0')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(sec_banner)
            story.append(Spacer(1, 4))
        elif line.startswith('### '): 
            story.append(Paragraph(clean_markdown_text(line[4:]), sub_style))
        elif line.startswith('- '): 
            cleaned_line = clean_markdown_text(line[2:])
            story.append(Paragraph(f"• {cleaned_line}", body_style))
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

# 5. AI 실행 및 화면(웹사이트) 출력
if submitted:
    if not name: 
        st.warning("성명을 입력해주세요.")
    else:
        with st.spinner("인문교양 학습 및 심층적 사유 고도화 방향에 맞추어 종합 분석 리포트를 생성 중입니다... (약 20~30초 소요)"):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 수석 인문학 교육 컨설턴트 및 철학적 사고 고도화 전문가
            # GOAL & OBJECTIVES:
            본 컨설팅 리포트는 다음의 세 가지 핵심 목표를 달성하도록 작성되어야 합니다.
            1. 인문교양 학습: 폭넓은 독서와 역사, 철학, 문학적 소양을 체득하는 방안 제시.
            2. 토론 형식의 강의 수강: 일방향 주입식 학습을 넘어, 토론형 강의를 통한 타인과의 소통 및 다각적 시각 함양.
            3. 심층적인 생각의 고도화: 현상 이면의 본질을 꿰뚫어 보는 비판적이고 깊이 있는 사유 체계 구축.
            
            # RULES:
            1. 제공된 프로필과 인문학적 사유 척도 9개를 기반으로 아래 두 줄의 점수 데이터 먼저 출력:
               - 첫 번째 줄: 인지 성향 점수 5개 (개방성, 성실성, 외향성, 호감성, 정서안정성 / 0~100점)
               - 두 번째 줄: 인문 학습 역량 점수 5개 (비판적독해력, 토론설득력, 다원적공감력,철학적통찰력,사유고도화력 / 0~100점)
               를 각각 쉼표로 구분하여 숫자만 작성할 것. (예: 85,75,70,80,90 / 80,75,85,90,88)
            2. 본문 내용은 반드시 '인문교양 학습', '토론형 강의 활용', '심층 사유 고도화'라는 목적에 초점을 맞추어 서술할 것.
            3. 아래 OUTPUT FORMAT의 마크다운(##) 구조를 정확히 준수할 것.
            
            # OUTPUT FORMAT:
            85,75,70,80,90
            80,75,85,90,88
            ## 인문교양 학습 및 지적 호기심 분석
            - **인문적 사유의 원천과 교양 학습 태도**: (인문교양 학습 목적에 맞추어 상세 기술)
            - **텍스트 심층 독해 및 철학적 성향**: (심층적 생각 고도화 관점에서 상세 기술)
            - **지적 성장을 저해하는 표피적 사고 요인**: (고도화를 위한 장애물 분석)
            
            ## 토론형 강의 및 소통 역량 진단
            - **토론 형식 강의 수강 시의 강점**: (토론형 강의 활용 방안 상세 기술)
            - **다원적 관점 수용과 논리적 설득력**: (타인과의 상호작용 측면 기술)
            - **그룹 토론에서의 심층 소통 전략**: (소통 심화 방안 제시)
            
            ## 심층 생각 고도화 액션 플랜표
            | 학습 영역 | 현재 사유 수준 진단 | 심층적 사고 고도화 실행 방안 |
            | :--- | :--- | :--- |
            | **인문교양 심화 학습** | (구체적 내용 기술) | (구체적 액션 기술) |
            | **토론형 강의 몰입** | (구체적 내용 기술) | (구체적 액션 기술) |
            | **메타인지 및 사유 확장** | (구체적 내용 기술) | (구체적 액션 기술) |
            
            ## Master Action Plan for Deep Thinking
            - **고전 및 인문교양 원서 정독 프로젝트 수행**: (구체적 시나리오 제시)
            - **소크라테스식 토론형 강의 및 세미나 적극 참여**: (방법론 제시)
            - **사유의 깊이를 더하는 비판적 에세이 작성 및 피드백**: (필요성 설명)
            """
            
            user_data = f"- 이름: {name}, 관심분야: {job}\n- MBTI: {mbti}, 생년월일: {birth}, 혈액형: {blood_type}\n- 인문사유척도: 본질탐구({e1}),공감({e2}),성취({e3}),독창({e4}),심층분석({e5}),책임({e6}),열정({e7}),토론결단({e8}),조화({e9})"
            
            response = client.chat.completions.create(model="gpt-4o-mini", temperature=0.6, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_data}])
            raw_response = response.choices[0].message.content.strip()
            
            # 응답 데이터 파싱
            lines = raw_response.split('\n')
            try:
                big5_scores = [int(s.strip()) for s in lines[0].split(',')]
                sw_scores = [int(s.strip()) for s in lines[1].split(',')]
                
                if len(big5_scores) == 5 and len(sw_scores) == 5:
                    report_content = '\n'.join(lines[2:]).strip()
                else:
                    raise ValueError
            except:
                big5_scores = [85, 75, 70, 80, 75]
                sw_scores = [80, 85, 75, 90, 88]
                report_content = raw_response
            
            st.success("✅ 파란색 테마 및 인문교양 심층 사고 고도화 목적이 반영된 리포트가 생성되었습니다.")
            
            # 웹 화면에 동일한 결과 출력
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            for line in report_content.split('\n'):
                line = line.strip()
                if not line: continue
                if line.startswith('## '):
                    st.markdown(f"### {line[3:]}")
                elif line.startswith('- '):
                    clean_txt = clean_markdown_text(line[2:])
                    st.markdown(f"- {clean_txt}")
                else:
                    st.markdown(clean_markdown_text(line))
            st.markdown("</div>", unsafe_allow_html=True)
            
            # PDF 파일 생성 및 다운로드 버튼 제공
            pdf_file = create_pdf(report_content, name, [e1, e2, e3, e4, e5, e6, e7, e8, e9], big5_scores, sw_scores)
            with open(pdf_file, "rb") as f:
                st.download_button("📕 파란색 테마 인문교양 컨설팅 PDF 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
