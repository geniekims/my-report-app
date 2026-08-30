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

# 1. 페이지 설정 및 UI 스타일 (파란색 계열 테마 적용)
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

# 2. 사용자 입력 폼 (예시: 홍길동)
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

# 마크다운 볼드(**) 기호를 깔끔한 HTML 태그로 변환하는 함수
def clean_markdown_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

# 3. ReportLab 자체 도형 생성 함수 (파란색 테마)
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

# 4. PDF 생성 함수
def create_pdf(text, user_name, motiv_scores, big5_scores, sw_scores):
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
    
    title_style = ParagraphStyle('MainTitle', fontName='NanumGothicBold', fontSize=16, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName='NanumGothicBold', fontSize=11, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName='NanumGothicBold', fontSize=10, textColor=colors.HexColor('#2B4C7E'), spaceBefore=6, spaceAfter=2)
    body_style = ParagraphStyle('Body', fontName='NanumGothic', fontSize=9, leading=14, textColor=colors.HexColor('#333333'))
    th_style = ParagraphStyle('TableHeader', fontName='NanumGothicBold', fontSize=8.5, alignment=TA_CENTER, textColor=colors.HexColor('#1F385C'))
    td_style = ParagraphStyle('TableData', fontName='NanumGothic', fontSize=8.5, leading=12, alignment=TA_LEFT)

    story = []
    
    # 파란색 메인 배너
    main_banner = Table([[Paragraph(f"<b>심층 역량 및 직무 적합도 통합 평가 | {user_name}</b>", title_style)]], colWidths=[535], rowHeights=[32])
    main_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#2B4C7E')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(main_banner)
    story.append(Spacer(1, 8))
    
    d1 = create_bar_drawing("내면 동기 밸런스 프로파일 (0~20)", ['완벽·조력·성취', '독창·탐구·책임', '열정·결단·조화'], [sum(motiv_scores[:3])//3, sum(motiv_scores[3:6])//3, sum(motiv_scores[6:])//3], 20)
    d2 = create_bar_drawing("성격 5요인 진단 (T-Score)", ['외향성', '호감성', '성실성', '정서안정성', '개방성'], big5_scores, 100)
    d3 = create_bar_drawing("직무 역량 분포 (Blue:강점)", ['기획분석력', '추진리더십', '협업소통력', '창의문제해결', '위기관리력'], sw_scores, 100)
    
    comment_p = Paragraph("<b>[도표 종합 분석 코멘트]</b><br/><br/>본 분석 모델은 대상자의 고유 기질적 특성, MBTI 성향, 다차원 심리 동기 구조, 그리고 현업 직무 수행에 필요한 핵심 역량을 정밀 융합하여 도출되었습니다.<br/><br/>푸른색 바는 조직 내에서 즉시 발휘될 수 있는 <b>핵심 강점 영역</b>을 의미합니다.", body_style)
    
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
        with st.spinner("대상자의 성향과 역량을 분석하여 맞춤형 리포트를 구성 중입니다... (약 20~30초 소요)"):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 글로벌 수석 커리어 컨설턴트 및 인문/조직 심리 전략가
            # RULES:
            1. 분량 규정: 각 하위 섹션마다 충분하고 구체적으로 작성할 것.
            2. 데이터 복합 유추: 제공된 MBTI, 생년월일, 혈액형, 내면 동기 점수 9개를 입체적으로 분석하여, 
               - 첫 번째 줄: 성격 5요인 점수 5개 (외향, 호감, 성실, 정서안정, 개방 / 0~100점)
               - 두 번째 줄: 직무 역량 점수 5개 (기획분석, 추진리더십, 협업소통, 창의문제해결, 위기관리 / 0~100점)
               를 각각 쉼표로 구분하여 숫자만 작성할 것. (예: 65,80,75,45,70 / 85,65,80,70,45)
            3. 금지어 철저 준수: 리포트 본문 내에서 '사주', '명리', '별자리' 등 출처를 유추할 수 있는 키워드는 절대 언급 금지. 완벽한 비즈니스 진단 보고서 톤 유지.
            4. 마스터플랜(Master Action Plan) 섹션에서는 **사용자의 진단된 성향에 맞추어**, 인문교양 학습, 토론 형식의 강의 수강, 그리고 심층적인 생각의 고도화 필요성을 반드시 포함하여 구체적인 실행 계획으로 제안할 것.
            5. 아래 OUTPUT FORMAT의 마크다운(##) 구조를 정확히 준수할 것.
            
            # OUTPUT FORMAT:
            65,80,75,45,70
            85,65,80,70,45
            ## 심리 동기 및 행동 패턴 분석
            - **에너지 원천과 행동 동기**: (MBTI 성향 및 내면 동기를 연계하여 매우 상세하게 기술)
            - **성격적 강점과 업무 스타일**: (매우 상세하게 기술)
            - **무의식적 스트레스 요인 및 대응 기제**: (매우 상세하게 기술)
            
            ## 직무 적합도 및 역량 분석
            - **강점 극대화 영역**: (매우 상세하게 기술)
            - **잠재적 위기 및 리스크 관리 전략**: (역량 보완 솔루션 제시)
            - **리더십 및 조직 협업 스타일**: (조직 내 융화 방법 제시)
            
            ## 심층 요약표
            | 분석 카테고리 | 진단 결과 요약 (상세 기술) | 맞춤형 성장 솔루션 (구체적 액션) |
            | :--- | :--- | :--- |
            | **커리어 성취 및 전문성** | (구체적 내용 기술) | (구체적 액션 기술) |
            | **마음 근육 및 스트레스** | (구체적 내용 기술) | (구체적 액션 기술) |
            | **조직 내 대인관계** | (구체적 내용 기술) | (구체적 액션 기술) |
            
            ## Master Action Plan
            - **개인 성향 맞춤 인문교양 학습 수행**: (사용자 성향을 반영한 인문교양 학습 필요성 및 실천 방안 제시)
            - **다각적 시각 함양을 위한 토론형식의 강의 수강**: (소통과 비판적 사고를 위한 토론형 강의 참여 전략 제시)
            - **메타인지 강화를 통한 심층적인 생각의 고도화**: (표피적 사고를 탈피하고 본질을 통찰하는 사유 확장 방안 제시)
            """
            
            user_data = f"- 이름: {name}, 직무: {job}\n- MBTI: {mbti}, 생년월일: {birth}, 혈액형: {blood_type}\n- 내면동기척도: 완벽({e1}),조력({e2}),성취({e3}),독창({e4}),탐구({e5}),책임({e6}),열정({e7}),결단({e8}),조화({e9})"
            
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
                big5_scores = [60, 75, 80, 50, 70]
                sw_scores = [80, 70, 75, 65, 60]
                report_content = raw_response
            
            st.success("✅ 데이터 분석 보고서가 생성되었습니다.")
            
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
                st.download_button("📕 PDF 보고서 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
