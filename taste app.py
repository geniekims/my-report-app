import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import plotly.graph_objects as go

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
    st.markdown("### 👤 기본 프로필 (명리/별자리 분석 기반)")
    col1, col2, col3, col4 = st.columns(4)
    with col1: name = st.text_input("성명", placeholder="예: 주진희")
    with col2: birth = st.date_input("생년월일 (사주 베이스)", value=datetime.date(1990, 1, 1))
    with col3: zodiac = st.text_input("별자리", placeholder="예: 황소자리")
    with col4: job = st.text_input("직무/전공", placeholder="예: 데이터 분석가")
    
    st.markdown("---")
    st.markdown("### 📊 [도표 1] 다차원 성향 척도 (0~20점)")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        e1 = st.number_input("1번 (완벽/원칙)", 0, 20, 15)
        e4 = st.number_input("4번 (개성/창의)", 0, 20, 12)
        e7 = st.number_input("7번 (열정/비전)", 0, 20, 10)
    with col_e2:
        e2 = st.number_input("2번 (조력/공감)", 0, 20, 14)
        e5 = st.number_input("5번 (탐구/분석)", 0, 20, 18)
        e8 = st.number_input("8번 (도전/결단)", 0, 20, 11)
    with col_e3:
        e3 = st.number_input("3번 (성취/목표)", 0, 20, 16)
        e6 = st.number_input("6번 (충성/책임)", 0, 20, 13)
        e9 = st.number_input("9번 (평화/수용)", 0, 20, 9)

    st.markdown("---")
    st.markdown("### 📉 [도표 3] 직무 핵심 역량 강약점 (0~100점)")
    st.caption("※ 도표 2(직업선호도 L형 성격)는 입력된 생년월일, 별자리, 성향 척도를 AI가 종합 분석하여 자동으로 도출합니다.")
    col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
    with col_c1: c_ana = st.slider("기획 및 분석력", 0, 100, 85)
    with col_c2: c_lea = st.slider("추진력 및 리더십", 0, 100, 65)
    with col_c3: c_com = st.slider("소통 및 협업능력", 0, 100, 80)
    with col_c4: c_cre = st.slider("창의적 문제해결", 0, 100, 70)
    with col_c5: c_det = st.slider("꼼꼼함 및 위기관리", 0, 100, 45)
    
    submitted = st.form_submit_button("A4 2페이지 분량 평가 보고서 생성", use_container_width=True)

# 3. 도표(차트) 생성 함수들
def create_radar_chart(scores, save_path):
    categories = ['1번(완벽)', '2번(조력)', '3번(성취)', '4번(개성)', '5번(탐구)', '6번(충성)', '7번(열정)', '8번(도전)', '9번(평화)']
    fig = go.Figure(data=[go.Scatterpolar(r=[*scores, scores[0]], theta=[*categories, categories[0]], fill='toself', line_color='#2B4C7E', fillcolor='rgba(43, 76, 126, 0.2)')])
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 20])), showlegend=False, title=dict(text="다차원 성향 밸런스", font=dict(size=14, color="#2B4C7E")), margin=dict(l=30, r=30, t=40, b=20), paper_bgcolor='white')
    fig.write_image(save_path, width=400, height=300, scale=2)

def create_big5_chart(scores, save_path):
    traits = ['외향성', '호감성', '성실성', '불안정성', '경험개방성']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=scores, y=traits, mode='lines+markers', marker=dict(size=12, color='#1F385C'), line=dict(color='#4A70B0', width=3)))
    fig.update_layout(xaxis=dict(range=[0, 100], title="T-Score"), title=dict(text="L형 성격 5요인 (AI 종합 도출)", font=dict(size=14, color="#2B4C7E")), margin=dict(l=80, r=20, t=40, b=30), paper_bgcolor='white')
    fig.write_image(save_path, width=400, height=300, scale=2)

def create_sw_chart(scores, save_path):
    categories = ['분석력', '추진력', '협업능력', '창의성', '위기관리']
    colors = ['#2B4C7E' if s >= 60 else '#D9534F' for s in scores]
    fig = go.Figure(data=[go.Bar(x=scores, y=categories, orientation='h', marker_color=colors)])
    fig.update_layout(xaxis=dict(range=[0, 100]), title=dict(text="직무 역량 도표 (Blue:강점, Red:보완)", font=dict(size=14, color="#2B4C7E")), margin=dict(l=80, r=20, t=40, b=30), paper_bgcolor='white')
    fig.write_image(save_path, width=400, height=300, scale=2)

# 4. PDF 생성 (A4 2페이지 레이아웃)
def create_pdf(text, user_name, chart1, chart2, chart3):
    filename = f"{user_name}_Assessment_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=35, leftMargin=35, topMargin=40, bottomMargin=40)
    
    font_path, bold_path = "NanumGothic.ttf", "NanumGothicBold.ttf"
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
    
    chart_table = Table([
        [Image(chart1, width=255, height=190), Image(chart2, width=255, height=190)],
        [Image(chart3, width=255, height=190), Paragraph("<b>[도표 종합 분석 코멘트]</b><br/><br/>본 평가의 분석 모델은 대상자의 내면적 동기, 생년월일 기반의 기질적 특성, 그리고 현재 발현되고 있는 직무 핵심 역량을 입체적으로 융합하여 도출되었습니다.<br/><br/>푸른색 그래프는 조직 내에서 즉시 발휘될 수 있는 <b>핵심 강점</b>을 의미하며, 붉은색으로 표시된 역량 영역은 지속적인 모니터링 및 <b>리스크 관리</b>가 필요한 영역을 나타냅니다.", body_style)]
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
        with st.spinner("사주, 별자리, 성향 데이터를 복합 분석하여 L형 성격 요인을 도출하고 보고서를 작성 중입니다... (약 20~30초 소요)"):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 글로벌 수석 커리어 컨설턴트 및 명리학/조직 심리 전략가
            # RULES:
            1. 분량 규정: 반드시 A4 2페이지 분량이 꽉 찰 수 있도록 각 하위 섹션마다 최소 500자 이상 구체적으로 작성할 것.
            2. 데이터 융합 분석: 제공받은 사용자의 생년월일(사주 명리 기반 기질), 별자리, 다차원 성향(에니어그램)을 내부적으로 종합 분석하여, '직업선호도 L형 성격 5요인(외향성, 호감성, 성실성, 불안정성, 경험개방성)' 점수를 0~100점 사이로 자체 추론(도출)할 것.
            3. 금지어: 리포트 본문 내에서는 '사주', '에니어그램', '별자리', '혈액형' 단어를 절대 직접 언급하지 말 것. (심리 평가 및 기질 분석을 진행한 것처럼 전문적인 비즈니스 용어로 치환)
            4. ★매우 중요★: AI의 응답 가장 첫 번째 줄에는 반드시 AI가 도출해 낸 L형 성격 5요인 점수 5개를 쉼표(,)로 구분하여 숫자만 작성할 것. (예: 65, 80, 75, 45, 70)
            5. 두 번째 줄부터 아래 OUTPUT FORMAT의 마크다운(##)을 정확히 따라 본격적인 보고서를 작성할 것.
            
            # OUTPUT FORMAT:
            [첫 줄은 반드시 점수 5개 작성]
            ## 심리 동기 및 성격 5요인 분석
            - **에너지 원천과 행동 동기**: (매우 상세하게 3~4문장 이상)
            - **성격적 강점과 업무 스타일**: (매우 상세하게 3~4문장 이상)
            - **무의식적 방어기제 및 스트레스 취약성**: (매우 상세하게)
            
            ## 직무 적합도 및 역량 분석
            - **강점 극대화 영역**: (매우 상세하게)
            - **잠재적 위기 및 리스크 관리 전략**: (약점 보완에 대한 심도 깊은 솔루션 제시)
            - **리더십 및 팔로워십 스타일**: (조직 내 융화 및 주도성 발휘 방법)
            
            ## 심층 요약표
            | 분석 카테고리 | 진단 결과 요약 (상세 기술) | 맞춤형 성장 솔루션 (구체적 액션) |
            | :--- | :--- | :--- |
            | **커리어 성취 및 전문성** | ... | ... |
            | **마음 근육 및 스트레스** | ... | ... |
            | **조직 내 대인관계** | ... | ... |
            
            ## Master Action Plan
            - **전략적 네트워킹 및 멘토링 세션 참여**: (어떻게 참여하고 누구를 만날지 구체적 시나리오 제시)
            - **실무 성과 가속화를 위한 몰입형 프로젝트 설계**: (어떤 프로젝트를 리딩할 것인지 방법론 제시)
            - **인문학 및 고전 교육 이수를 통한 멘탈리티 강화**: (통찰력 확장에 왜 필요한지 설명)
            """
            
            user_data = f"- 이름: {name}, 직업: {job}\n- 생년월일(사주): {birth}, 별자리: {zodiac}\n- 다차원성향(에니어그램): 1번({e1}),2번({e2}),3번({e3}),4번({e4}),5번({e5}),6번({e6}),7번({e7}),8번({e8}),9번({e9})\n- 직무역량: 분석({c_ana}),추진({c_lea}),소통({c_com}),창의({c_cre}),꼼꼼({c_det})"
            
            response = client.chat.completions.create(model="gpt-4o-mini", temperature=0.6, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_data}])
            raw_response = response.choices[0].message.content.strip()
            
            # 응답 텍스트 파싱: 첫 줄(AI가 도출한 Big 5 점수)과 나머지 보고서 분리
            lines = raw_response.split('\n')
            try:
                big5_scores = [int(s.strip()) for s in lines[0].split(',')]
                if len(big5_scores) == 5:
                    b_ext, b_agr, b_con, b_neu, b_ope = big5_scores
                    report_content = '\n'.join(lines[1:]).strip()
                else:
                    raise ValueError
            except:
                # 파싱 실패 시 기본값 세팅 및 텍스트 원복
                b_ext, b_agr, b_con, b_neu, b_ope = [50, 50, 50, 50, 50]
                report_content = raw_response
            
            # 차트 이미지 생성
            chart1_path, chart2_path, chart3_path = "c1.png", "c2.png", "c3.png"
            create_radar_chart([e1, e2, e3, e4, e5, e6, e7, e8, e9], chart1_path)
            create_big5_chart([b_ext, b_agr, b_con, b_neu, b_ope], chart2_path)
            create_sw_chart([c_ana, c_lea, c_com, c_cre, c_det], chart3_path)
            
            st.success("✅ A4 2페이지 분량의 심층 보고서가 성공적으로 생성되었습니다.")
            
            # 화면 출력용
            with st.expander("생성된 보고서 텍스트 미리보기"):
                st.markdown(report_content)
            
            pdf_file = create_pdf(report_content, name, chart1_path, chart2_path, chart3_path)
            with open(pdf_file, "rb") as f:
                st.download_button("📕 신용평가형 2Page PDF 보고서 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
