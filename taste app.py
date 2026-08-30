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
    st.markdown("### 👤 기본 프로필")
    col1, col2, col3, col4 = st.columns(4)
    with col1: name = st.text_input("성명", placeholder="예: 주진희")
    with col2: birth = st.date_input("생년월일", value=datetime.date(1990, 1, 1))
    with col3: gender = st.radio("성별", ["남성", "여성"])
    with col4: job = st.text_input("직무/전공", placeholder="예: 데이터 분석가")
    
    st.markdown("---")
    st.markdown("### 📊 [도표 1] 다차원 성향 척도 (에니어그램)")
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
    st.markdown("### 📈 [도표 2] 직업선호도 L형 성격 5요인 (0~100점)")
    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
    with col_b1: b_ext = st.slider("외향성", 0, 100, 60)
    with col_b2: b_agr = st.slider("호감성", 0, 100, 75)
    with col_b3: b_con = st.slider("성실성", 0, 100, 85)
    with col_b4: b_neu = st.slider("정서적 불안정성", 0, 100, 40)
    with col_b5: b_ope = st.slider("경험 개방성", 0, 100, 70)

    st.markdown("---")
    st.markdown("### 📉 [도표 3] 직무 핵심 역량 (강점 및 단점 / 0~100점)")
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
    fig.update_layout(xaxis=dict(range=[0, 100], title="T-Score"), title=dict(text="L형 성격 5요인 프로파일", font=dict(size=14, color="#2B4C7E")), margin=dict(l=80, r=20, t=40, b=30), paper_bgcolor='white')
    fig.write_image(save_path, width=400, height=300, scale=2)

def create_sw_chart(scores, save_path):
    categories = ['분석력', '추진력', '협업능력', '창의성', '위기관리']
    colors = ['#2B4C7E' if s >= 60 else '#D9534F' for s in scores] # 60 미만은 붉은색(약점)으로 표시
    fig = go.Figure(data=[go.Bar(x=scores, y=categories, orientation='h', marker_color=colors)])
    fig.update_layout(xaxis=dict(range=[0, 100]), title=dict(text="강점 및 약점 도표 (Blue:강점, Red:보완)", font=dict(size=14, color="#2B4C7E")), margin=dict(l=80, r=20, t=40, b=30), paper_bgcolor='white')
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
    
    # [1] 메인 타이틀
    main_banner = Table([[Paragraph(f"<b>심층 역량 및 직무 적합도 통합 평가 | {user_name}</b>", title_style)]], colWidths=[525], rowHeights=[40])
    main_banner.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4A70B0')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(main_banner)
    story.append(Spacer(1, 15))
    
    # [2] 3개의 도표를 그리드 형태로 배치
    chart_table = Table([
        [Image(chart1, width=255, height=190), Image(chart2, width=255, height=190)],
        [Image(chart3, width=255, height=190), Paragraph("<b>[도표 종합 분석 코멘트]</b><br/><br/>좌측 도표들은 평가 대상자의 내면적 동기(에니어그램), L형 성격 5요인(Big 5), 그리고 직무 수행에 필요한 핵심 역량의 강약점을 시각화한 결과입니다.<br/><br/>푸른색 그래프는 조직 내에서 즉시 발휘될 수 있는 <b>핵심 강점(우량/양호)</b>을 의미하며, 붉은색으로 표시된 역량 영역은 지속적인 모니터링 및 <b>리스크 관리(미흡)</b>가 필요한 영역을 나타냅니다.", body_style)]
    ], colWidths=[262.5, 262.5])
    chart_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('BOTTOMPADDING', (0,0), (-1,-1), 15)]))
    story.append(chart_table)
    story.append(Spacer(1, 10))

    # [3] AI 마크다운 텍스트 파싱 및 2페이지 강제 분할 로직
    table_data = []
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        # '심층 요약표' 또는 'Master Action Plan' 등장 시 두 번째 페이지로 넘김
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
        with st.spinner("다차원 데이터를 정밀 분석하여 A4 2페이지 분량의 심층 리포트를 작성하고 있습니다... (약 20~30초 소요)"):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            # 차트 이미지 생성
            chart1_path, chart2_path, chart3_path = "c1.png", "c2.png", "c3.png"
            create_radar_chart([e1, e2, e3, e4, e5, e6, e7, e8, e9], chart1_path)
            create_big5_chart([b_ext, b_agr, b_con, b_neu, b_ope], chart2_path)
            create_sw_chart([c_ana, c_lea, c_com, c_cre, c_det], chart3_path)
            
            system_prompt = """
            # ROLE: 글로벌 수석 커리어 컨설턴트 및 조직 심리 전략가
            # RULES:
            1. 분량 규정: 반드시 A4 2페이지 분량이 꽉 찰 수 있도록, 각 하위 섹션마다 최소 500자 이상, 매우 구체적인 예시와 행동 지침을 포함하여 '대폭 늘려서' 작성할 것. (총 2500자 이상)
            2. '사주', '에니어그램', '별자리', '혈액형' 단어 사용 금지.
            3. '인문학', '고전' 단어는 1~4번 섹션에서 금지.
            4. 각 섹션 대제목은 아래 OUTPUT FORMAT의 마크다운(##)을 정확히 따를 것.
            
            # OUTPUT FORMAT (마크다운 엄수):
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
            
            user_data = f"- 이름: {name}, 직업: {job}\n- 척도1: {e1},{e2},{e3},{e4},{e5},{e6},{e7},{e8},{e9}\n- 척도2(Big5): 외향({b_ext}),호감({b_agr}),성실({b_con}),불안({b_neu}),개방({b_ope})\n- 척도3(역량): 분석({c_ana}),추진({c_lea}),소통({c_com}),창의({c_cre}),꼼꼼({c_det})"
            
            response = client.chat.completions.create(model="gpt-4o-mini", temperature=0.5, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_data}])
            report_content = response.choices[0].message.content
            
            st.success("✅ A4 2페이지 분량의 심층 보고서가 성공적으로 생성되었습니다.")
            
            pdf_file = create_pdf(report_content, name, chart1_path, chart2_path, chart3_path)
            with open(pdf_file, "rb") as f:
                st.download_button("📕 신용평가형 2Page PDF 보고서 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
