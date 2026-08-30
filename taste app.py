import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 설정 및 UI 스타일 (신용평가보고서 딥블루 테마)
st.set_page_config(page_title="Executive Intelligence Report", page_icon="💼", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stApp { max-width: 900px; margin: 0 auto; }
    h1, h2, h3 { color: #2B4C7E; font-weight: bold; }
    .report-container {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 0px;
        border: 1px solid #B4C6E7;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #2B4C7E;
        color: white;
        border-radius: 4px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.2rem;
    }
    .stButton>button:hover { background-color: #1F385C; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2B4C7E; background-color:#E9EEF5; padding:20px; border-radius:8px;'>심층 역량 평가 보고서</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #5B7290;'>다차원 심리 동기 구조 및 커리어 성공 전략 통합 진단</p>", unsafe_allow_html=True)

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.markdown("### 👤 진단 대상자 프로필")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: name = st.text_input("성명", placeholder="예: 홍길동")
    with col2: birth = st.date_input("생년월일", min_value=datetime.date(1930, 1, 1), value=datetime.date(1990, 1, 1))
    with col3: gender = st.radio("성별", ["남성", "여성", "선택 안함"])
        
    col4, col5, col6, col7 = st.columns(4)
    with col4: blood_type = st.selectbox("혈액형", ["A형", "B형", "O형", "AB형"])
    with col5: zodiac = st.text_input("별자리", placeholder="예: 황소자리")
    with col6: mbti = st.text_input("MBTI", placeholder="예: INTJ")
    with col7: job = st.text_input("직무/전공", placeholder="예: 기획총괄")
    
    st.markdown("---")
    st.markdown("### 📊 세부 척도 점수 입력")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        e1 = st.number_input("1번 (완벽주의자)", min_value=0, max_value=20, value=0)
        e4 = st.number_input("4번 (개인주의자)", min_value=0, max_value=20, value=0)
        e7 = st.number_input("7번 (열정가)", min_value=0, max_value=20, value=0)
    with col_e2:
        e2 = st.number_input("2번 (조력자)", min_value=0, max_value=20, value=0)
        e5 = st.number_input("5번 (탐구자)", min_value=0, max_value=20, value=0)
        e8 = st.number_input("8번 (도전자)", min_value=0, max_value=20, value=0)
    with col_e3:
        e3 = st.number_input("3번 (성취가)", min_value=0, max_value=20, value=0)
        e6 = st.number_input("6번 (충실가)", min_value=0, max_value=20, value=0)
        e9 = st.number_input("9번 (평화주의자)", min_value=0, max_value=20, value=0)
    
    submitted = st.form_submit_button("평가 보고서 생성", use_container_width=True)

# 3. 방사형 차트 생성 및 저장 함수
def create_radar_chart(scores, save_path=None):
    categories = ['1번(완벽)', '2번(조력)', '3번(성취)', '4번(개성)', '5번(탐구)', '6번(충성)', '7번(열정)', '8번(도전)', '9번(평화)']
    categories = [*categories, categories[0]]
    plot_scores = [*scores, scores[0]]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=plot_scores,
                theta=categories,
                fill='toself',
                name='역량 프로파일',
                line_color='#2B4C7E',
                fillcolor='rgba(43, 76, 126, 0.2)'
            )
        ]
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 20], color="#B4C6E7"), angularaxis=dict(color="#5B7290")),
        showlegend=False,
        title=dict(text="다차원 성향 밸런스 도표", font=dict(size=16, color="#2B4C7E")),
        margin=dict(l=40, r=40, t=50, b=30),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    if save_path:
        try:
            fig.write_image(save_path, width=500, height=350, scale=2)
        except Exception as e:
            st.warning("차트를 PDF에 삽입하려면 'kaleido' 패키지가 필요합니다.")
            
    return fig

# 4. 브로슈어형(신용평가보고서 테마) PDF 생성 함수
def create_pdf(text, user_name, chart_path):
    filename = f"{user_name}_Assessment_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=35, leftMargin=35, topMargin=40, bottomMargin=40)
    
    font_path = "NanumGothic.ttf"
    bold_path = "NanumGothicBold.ttf"
    if not os.path.exists(bold_path): bold_path = font_path
        
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_path))
        font_name, bold_name = 'NanumGothic', 'NanumGothicBold'
    except:
        font_name, bold_name = 'Helvetica', 'Helvetica-Bold'
    
    # 보고서 전용 스타일 정의
    title_style = ParagraphStyle('MainTitle', fontName=bold_name, fontSize=18, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName=bold_name, fontSize=12, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName=bold_name, fontSize=11, textColor=colors.HexColor('#2B4C7E'), spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('Body', fontName=font_name, fontSize=9.5, leading=16, textColor=colors.HexColor('#333333'))
    th_style = ParagraphStyle('TableHeader', fontName=bold_name, fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#1F385C'))
    td_style = ParagraphStyle('TableData', fontName=font_name, fontSize=9, leading=13, alignment=TA_LEFT)

    story = []
    
    # 메인 타이틀 배너 (풀사이즈 딥블루)
    main_banner = Table([[Paragraph(f"<b>심층 역량 평가 보고서 | {user_name}</b>", title_style)]], colWidths=[525], rowHeights=[40])
    main_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#4A70B0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(main_banner)
    story.append(Spacer(1, 15))
    
    # 도표(차트) 삽입
    if os.path.exists(chart_path):
        story.append(Image(chart_path, width=400, height=280))
        story.append(Spacer(1, 15))

    # 마크다운 파싱 및 테이블 구성 로직
    table_data = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 테이블 처리 로직
        if line.startswith('|'):
            if '---' in line: continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            
            row_cells = []
            for col in cols:
                # 첫 번째 행은 헤더 스타일, 나머지는 데이터 스타일
                if len(table_data) == 0:
                    row_cells.append(Paragraph(f"<b>{col}</b>", th_style))
                else:
                    row_cells.append(Paragraph(col, td_style))
            table_data.append(row_cells)
            continue
        
        # 테이블이 끝났을 때 렌더링
        if table_data:
            t = Table(table_data, colWidths=[100, 190, 235]) # 컬럼 너비 비율
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDE6F0')), # 테이블 헤더 배경 (연한 블루)
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B4C6E7')), # 연한 블루그레이 격자선
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F4F7FB')), # 첫 번째 열 배경색 구분
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
            table_data = [] # 초기화

        # 일반 텍스트 및 헤딩 처리
        if line.startswith('## '):
            story.append(Spacer(1, 10))
            # 딥블루 서브 배너
            sec_banner = Table([[Paragraph(line[3:], header_style)]], colWidths=[525], rowHeights=[25])
            sec_banner.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#5B80C2')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
            ]))
            story.append(sec_banner)
            story.append(Spacer(1, 8))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], sub_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {line[2:]}", body_style))
            story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(line, body_style))
            story.append(Spacer(1, 4))
            
    # 문서 마지막에 남아있는 테이블이 있다면 렌더링
    if table_data:
        t = Table(table_data, colWidths=[100, 190, 235])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDE6F0')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B4C6E7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F4F7FB')),
        ]))
        story.append(t)

    doc.build(story)
    return filename


# 5. AI 연동 및 실행 결과 출력
if submitted:
    if not name:
        st.warning("진단 대상자의 성명을 입력해주세요.")
    else:
        with st.spinner("다차원 데이터를 정밀 분석 및 시각화 리포트를 구성하고 있습니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), 6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            
            # 임시 차트 이미지 생성
            chart_img_path = "temp_radar_chart.png"
            radar_fig = create_radar_chart(enneagram_scores, save_path=chart_img_path)
            
            system_prompt = """
            # ROLE: 글로벌 수석 커리어 컨설턴트 및 조직 심리 전략가
            # RULES:
            1. '사주', '에니어그램', '별자리', '혈액형' 단어 사용 금지.
            2. '인문학', '고전' 단어는 1~4번 섹션에서 사용 금지.
            3. 마지막 'Master Action Plan'에서만 3가지 실행 액션 제시:
               - 1번째: 전략적 네트워킹 및 멘토링 세션 참여
               - 2번째: 실무 성과 가속화를 위한 몰입형 프로젝트 설계
               - 3번째: 인문학 및 고전 교육 이수
            4. 각 섹션 대제목은 매우 심플하게 작성(예: "심리 동기 분석").
            
            # OUTPUT FORMAT (마크다운 필수 엄수):
            ## 심리 동기 분석
            - **에너지 원천**: ...
            - **방어기제**: ...
            
            ## 커리어 로드맵
            - **강점 극대화 영역**: ...
            - **리스크 관리**: ...
            
            ## 심층 요약표
            | 분석 카테고리 | 진단 결과 요약 | 맞춤형 성장 솔루션 |
            | :--- | :--- | :--- |
            | **커리어 성취** | ... | ... |
            | **마음 근육** | ... | ... |
            | **개인 역량** | ... | ... |
            
            ## Master Action Plan
            - **전략적 네트워킹 및 멘토링 세션 참여**: ...
            - **실무 성과 가속화를 위한 몰입형 프로젝트 설계**: ...
            - **인문학 및 고전 교육 이수**: ...
            """
            
            user_prompt = f"- 이름: {name}\n- 직업(전공): {job}\n- 세부 성향 점수 분포: {enneagram_text}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.4,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            
            report_content = response.choices[0].message.content
            
            st.success("✅ 전문 심층 평가 보고서가 성공적으로 생성되었습니다.")
            
            with st.container():
                st.markdown("<div class='report-container'>", unsafe_allow_html=True)
                st.plotly_chart(radar_fig, use_container_width=True)
                st.markdown("---")
                st.markdown(report_content)
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("")
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button("📄 텍스트 리포트 (.txt)", data=report_content, file_name=f"{name}_Report.txt", mime="text/plain", use_container_width=True)
            with col_dl2:
                pdf_file = create_pdf(report_content, name, chart_img_path)
                with open(pdf_file, "rb") as f:
                    st.download_button("📕 신용평가형 PDF 보고서 (.pdf)", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
