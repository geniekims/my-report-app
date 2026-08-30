import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime

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
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2B4C7E; background-color:#E9EEF5; padding:20px; border-radius:8px;'>심층 역량 및 직무 적합도 평가 보고서</h1>", unsafe_allow_html=True)

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.markdown("### 👤 기본 프로필 및 심리 성향 진단")
    col1, col2, col3, col4 = st.columns(4)
    with col1: name = st.text_input("성명", placeholder="예: 주진희")
    with col2: birth = st.date_input("생년월일 (기질 및 별자리 자동 유추 기준)", value=datetime.date(1990, 1, 1))
    with col3: blood_type = st.selectbox("혈액형", ["A형", "B형", "O형", "AB형"])
    with col4: job = st.text_input("직무 / 전공", placeholder="예: 데이터 분석가")
    
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

    submitted = st.form_submit_button("A4 2페이지 분량 종합 평가 보고서 생성", use_container_width=True)

# 3. ReportLab 자체 도형 생성 함수 (외부 패키지 불필요)
def create_bar_drawing(title, categories, scores, max_val=100):
    d = Drawing(250, 160)
    d.add(Rect(0, 0, 250, 160, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#B4C6E7'), strokeWidth=0.5, rx=5, ry=5))
    d.add(String(15, 140, title, fontName='NanumGothicBold', fontSize=10, fillColor=colors.HexColor('#2B4C7E')))
    
    y = 115
    for cat, score in zip(categories, scores):
        d.add(String(15, y, cat, fontName='NanumGothic', fontSize=8, fillColor=colors.HexColor('#333333')))
        d.add(Rect(75, y+1, 120, 8, fillColor=colors.HexColor('#E2E8F0'), strokeColor=None))
        bar_width = (score / max_val) * 120
        bar_color = colors.HexColor('#2B4C7E') if score >= 60 else colors.HexColor('#D9534F')
        if max_val == 20: bar_color = colors.HexColor('#2B4C7E') # 동기는 모두 파란색
        d.add(Rect(75, y+1, bar_width, 8, fillColor=bar_color, strokeColor=None))
        d.add(String(200, y, f"{score}", fontName='NanumGothicBold', fontSize=8, fillColor=colors.HexColor('#333333')))
        y -= 22
    return d

# 4. PDF 생성 (A4 2페이지 레이아웃)
def create_pdf(text, user_name, motiv_scores, big5_scores, sw_scores):
    filename = f"{user_name}_Assessment_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=35, leftMargin=35, topMargin=40, bottomMargin=40)
    
    font_path = "NanumGothic.ttf"
    bold_path = "NanumGothicBold.ttf"
    if not os.path.exists(bold_path): bold_path = font_path
    pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
    pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_path))
    
    title_style = ParagraphStyle('MainTitle', fontName='NanumGothicBold', fontSize=18, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName='NanumGothicBold', fontSize=12, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName='NanumGothicBold', fontSize=11, textColor=colors.HexColor('#2B4C7E'), spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('Body', fontName='NanumGothic', fontSize=9.5, leading=16, textColor=colors.HexColor('#333333'))
    th_style = ParagraphStyle('TableHeader', fontName='NanumGothicBold', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#1F385C'))
    td_style = ParagraphStyle('TableData', fontName='NanumGothic', fontSize=9, leading=13, alignment=TA_LEFT)

    story = []
    
    main_banner = Table([[Paragraph(f"<b>심층 역량 및 직무 적합도 통합 평가 | {user_name}</b>", title_style)]], colWidths=[525], rowHeights=[40])
    main_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4A70B0')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(main_banner)
    story.append(Spacer(1, 15))
    
    # 지표 시각화 컴포넌트 배치
    d1 = create_bar_drawing("내면 동기 밸런스 프로파일 (0~20)", ['완벽·조력·성취', '독창·탐구·책임', '열정·결단·조화'], [sum(motiv_scores[:3])//3, sum(motiv_scores[3:6])//3, sum(motiv_scores[6:])//3], 20)
    d2 = create_bar_drawing("성성 5요인 진단 (T-Score)", ['외향성', '호감성', '성실성', '정서안정성', '개방성'], big5_scores, 100)
    d3 = create_bar_drawing("직무 역량 분포 (Blue:강점)", ['기획분석력', '추진리더십', '협업소통력', '창의문제해결', '위기관리력'], sw_scores, 100)
    
    comment_p = Paragraph("<b>[도표 종합 분석 코멘트]</b><br/><br/>본 분석 모델은 대상자의 고유 기질적 특성, 다차원 심리 동기 구조, 그리고 현업 직무 수행에 필요한 핵심 역량을 정밀 융합하여 도출되었습니다.<br/><br/>푸른색 바는 조직 내에서 즉시 발휘될 수 있는 <b>핵심 강점 영역</b>을 의미합니다.", body_style)
    
    chart_table = Table([
        [d1, d2],
        [d3, comment_p]
    ], colWidths=[262.5, 262.5])
    chart_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('BOTTOMPADDING', (0,0), (-1,-1), 15)]))
    story.append(chart_table)
    story.append(Spacer(1, 10))

    table_data = []
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('## 심층 요약표') or line.startswith('## Master Action Plan'):
            story.append(PageBreak()) 
            
        if line.startswith('|'):
            if '---' in line: continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            row_cells = [Paragraph(f"<b>{col}</b>", th_style) if len(table_data) == 0 else Paragraph(col, td_style) for col in cols]
            table_data.append(row_cells)
            continue
        
        if table_data:
            t = Table(table_data, colWidths=[100, 190, 235])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDE6F0')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B4C6E7')),
                ('TOPPADDING', (0,0), (-1,-1), 8), ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F4F7FB')),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
            table_data = []

        if line.startswith('## '):
            story.append(Spacer(1, 10))
            sec_banner = Table([[Paragraph(line[3:], header_style)]], colWidths=[525], rowHeights=[25])
            sec_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#5B80C2')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(sec_banner)
            story.append(Spacer(1, 8))
        elif line.startswith('### '): story.append(Paragraph(line[4:], sub_style))
        elif line.startswith('- '): story.append(Paragraph(f"• {line[2:]}", body_style)); story.append(Spacer(1, 4))
        else: story.append(Paragraph(line, body_style)); story.append(Spacer(1, 4))
            
    if table_data:
        t = Table(table_data, colWidths=[100, 190, 235])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDE6F0')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B4C6E7')), ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F4F7FB'))]))
        story.append(t)

    doc.build(story)
    return filename

# 5. AI 실행 및 출력
if submitted:
    if not name: st.warning("성명을 입력해주세요.")
    else:
        with st.spinner("대상자의 심층 데이터를 복합 분석하여 종합 리포트 및 지표를 구성 중입니다... (약 20~30초 소요)"):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 글로벌 수석 커리어 컨설턴트 및 조직 심리 전략가
            # RULES:
            1. 분량 규정: 반드시 A4 2페이지 분량이 꽉 찰 수 있도록 각 하위 섹션마다 최소 500자 이상 구체적으로 작성할 것.
            2. 데이터 자동 유추: 제공된 생년월일(생일 월/일을 통해 별자리 및 기질 자동 유추)과 혈액형, 내면 동기 점수 9개를 복합 분석하여, 
               - 첫 번째 줄: 성격 5요인 점수 5개 (외향, 호감, 성실, 정서안정, 개방 / 0~100점)
               - 두 번째 줄: 직무 역량 점수 5개 (기획분석, 추진리더십, 협업소통, 창의문제해결, 위기관리 / 0~100점)
               를 각각 쉼표로 구분하여 숫자만 작성할 것. (예: 65,80,75,45,70 / 85,65,80,70,45)
            3. 금지어 철저 준수: 리포트 본문 내에서 '사주', '명리', '별자리', '에니어그램' 등 출처를 유추할 수 있는 키워드는 절대 언급 금지. 완벽한 비즈니스 심리 진단 보고서 톤 유지.
            4. 아래 OUTPUT FORMAT의 마크다운(##) 구조를 정확히 준수할 것.
            
            # OUTPUT FORMAT:
            [첫 줄]: 성격 5요인 점수 5개 (예: 65,80,75,45,70)
            [둘째 줄]: 직무 역량 점수 5개 (예: 85,65,80,70,45)
            ## 심리 동기 및 행동 패턴 분석
            - **에너지 원천과 행동 동기**: (매우 상세하게 기술)
            - **성격적 강점과 업무 스타일**: (매우 상세하게 기술)
            - **무의식적 스트레스 요인 및 대응 기제**: (매우 상세하게 기술)
            
            ## 직무 적합도 및 역량 분석
            - **강점 극대화 영역**: (매우 상세하게 기술)
            - **잠재적 위기 및 리스크 관리 전략**: (역량 보완 솔루션 제시)
            - **리더십 및 조직 협업 스타일**: (조직 내 융화 방법 제시)
            
            ## 심층 요약표
            | 분석 카테고리 | 진단 결과 요약 (상세 기술) | 맞춤형 성장 솔루션 (구체적 액션) |
            | :--- | :--- | :--- |
            | **커리어 성취 및 전문성** | ... | ... |
            | **마음 근육 및 스트레스** | ... | ... |
            | **조직 내 대인관계** | ... | ... |
            
            ## Master Action Plan
            - **전략적 네트워킹 및 멘토링 세션 참여**: (구체적 시나리오 제시)
            - **실무 성과 가속화를 위한 몰입형 프로젝트 설계**: (방법론 제시)
            - **전문성 심화 교육 이수를 통한 통찰력 강화**: (필요성 설명)
            """
            
            user_data = f"- 이름: {name}, 직무: {job}\n- 생년월일: {birth}, 혈액형: {blood_type}\n- 내면동기척도: 완벽({e1}),조력({e2}),성취({e3}),독창({e4}),탐구({e5}),책임({e6}),열정({e7}),결단({e8}),조화({e9})"
            
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
            
            st.success("✅ A4 2페이지 분량의 심층 보고서가 성공적으로 생성되었습니다.")
            
            pdf_file = create_pdf(report_content, name, [e1, e2, e3, e4, e5, e6, e7, e8, e9], big5_scores, sw_scores)
            with open(pdf_file, "rb") as f:
                st.download_button("📕 신용평가형 2Page PDF 보고서 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
