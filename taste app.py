import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 설정 및 UI 스타일
st.set_page_config(page_title="Executive Intelligence Report", page_icon="💼", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stApp { max-width: 900px; margin: 0 auto; }
    h1, h2, h3 { color: #0F172A; }
    .report-container {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.2rem;
    }
    .stButton>button:hover { background-color: #1E40AF; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>💼 Executive Intelligence Report</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B;'>다차원 심리 동기 구조 및 커리어 성공 전략 통합 진단 플랫폼</p>", unsafe_allow_html=True)

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.markdown("### 👤 진단 대상자 기본 프로필")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        name = st.text_input("성명", placeholder="예: 홍길동")
    with col2:
        birth = st.date_input("생년월일", min_value=datetime.date(1930, 1, 1), value=datetime.date(1990, 1, 1))
    with col3:
        gender = st.radio("성별", ["남성", "여성", "선택 안함"])
        
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        blood_type = st.selectbox("혈액형", ["A형", "B형", "O형", "AB형"])
    with col5:
        zodiac = st.text_input("별자리", placeholder="예: 황소자리")
    with col6:
        mbti = st.text_input("MBTI", placeholder="예: INTJ")
    with col7:
        job = st.text_input("직무/전공", placeholder="예: 기획총괄")
    
    st.markdown("---")
    st.markdown("### 📊 심층 성향 프로파일 (에니어그램 세부 척도 점수)")
    
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
    
    submitted = st.form_submit_button("✨ 전문 심층 분석 리포트 생성", use_container_width=True)

# 3. 브로슈어/리포트 스타일 PDF 생성 함수 (ReportLab)
def create_pdf(text, user_name):
    filename = f"{user_name}_Executive_Report.pdf"
    doc = SimpleDocTemplate(
        filename, 
        pagesize=A4, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30
    )
    
    # 폰트 로드 설정 (NanumGothic 및 NanumGothicBold 준비 필요)
    font_path = "NanumGothic.ttf"
    bold_font_path = "NanumGothicBold.ttf"
    
    if not os.path.exists(bold_font_path):
        bold_font_path = font_path # 볼드가 없으면 일반 폰트로 대체
        
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_font_path))
        font_name = 'NanumGothic'
        bold_name = 'NanumGothicBold'
    except:
        font_name = 'Helvetica'
        bold_name = 'Helvetica-Bold'
        
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        fontName=bold_name,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#FFFFFF')
    )
    
    h_style = ParagraphStyle(
        'ReportHeader',
        fontName=bold_name,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        fontName=font_name,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    story = []
    
    # [디자인 요소 1] 상단 기업형 브랜드 배너 (네이비 컬러 바)
    header_table = Table([[Paragraph(f"<b>EXECUTIVE INTELLIGENCE REPORT | {user_name} 님 진단 결과서</b>", title_style)]], colWidths=[535], rowHeights=[32])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E3A8A')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # 본문 파싱 및 박스/테이블 형태 레이아웃 적용
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<b>{line[3:]}</b>", h_style))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], h_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {line[2:]}", body_style))
        elif line.startswith('|'):
            if '---' in line:
                continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 3:
                # [디자인 요소 2] 표 내부 항목을 깔끔한 그리드 박스 형태로 감싸기
                row_data = [
                    [Paragraph(f"<b>{cols[0]}</b>", body_style), 
                     Paragraph(f"{cols[1]}<br/><font color='#1E3A8A'><b>[Solution]</b> {cols[2]}</font>", body_style)]
                ]
                t = Table(row_data, colWidths=[120, 415])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t)
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(line, body_style))
            
    doc.build(story)
    return filename

# 4. 방사형 차트 생성
def create_radar_chart(scores):
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
                line_color='#1E3A8A',
                fillcolor='rgba(30, 58, 138, 0.12)'
            )
        ]
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 20], color="#94A3B8"), angularaxis=dict(color="#334155")),
        showlegend=False,
        title=dict(text="📊 다차원 내면 동기 및 성향 밸런스 매트릭스", font=dict(size=16, color="#0F172A")),
        margin=dict(l=50, r=50, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# 5. AI 연동 및 실행 결과 출력
if submitted:
    if not name:
        st.warning("진단 대상자의 성명을 입력해주세요.")
    else:
        with st.spinner("전문 컨설팅 엔진이 다차원 데이터를 정밀 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), 6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            
            system_prompt = """
            # ROLE: 글로벌 수석 커리어 컨설턴트 및 조직 심리 전략가
            # RULES:
            1. '사주', '에니어그램', '별자리', '혈액형' 단어 사용 금지.
            2. '인문학', '고전' 단어는 1~4번 섹션에서 사용 금지.
            3. 마지막 'Master Action Plan'에서만 3가지 실행 액션 제시:
               - 1번째: 전략적 네트워킹 및 멘토링 세션 참여
               - 2번째: 실무 성과 가속화를 위한 몰입형 프로젝트 설계
               - 3번째: 인문학 및 고전 교육 이수 (근본적 통찰과 멘탈 강화를 위한 필수성 상세 기술)
            4. 각 섹션 대제목은 심플하게 작성.
            
            # OUTPUT FORMAT:
            ## 🌟 [이름] 님 맞춤형 심층 분석 리포트
            ### 1. 심리 동기 분석
            - **에너지의 원천과 행동 동기**: ...
            - **무의식적 방어기제와 스트레스 유발 요인**: ...
            - **내면의 고유한 성향적 특징**: ...
            
            ### 2. 커리어 로드맵
            - **강점 극대화 영역 (주력 직무 매칭)**: ...
            - **잠재적 리스크 관리 전략**: ...
            - **조직 내 성과 창출을 위한 핵심 무기**: ...
            
            ### 3. 회복탄력성 솔루션
            - **번아웃 및 위기 시 심리적 반응 패턴**: ...
            - **내면 근육 강화 및 위기 대처법**: ...
            - **실패를 성장의 자양분으로 바꾸는 통찰력**: ...
            
            ### 4. 개인역량 향상 가이드
            - **직무 전문성 심화와 실행력 강화**: ...
            - **복잡한 문제 해결 및 전략적 사고**: ...
            - **균형 잡힌 사유를 통한 성과 확장**: ...
            
            | 분석 영역 | 핵심 진단 결과 (Depth Summary) | 맞춤형 성장 솔루션 (Prescription) |
            | :--- | :--- | :--- |
            | **커리어 및 성취** | ... | ... |
            | **마음 근육 (회복력)** | ... | ... |
            | **개인역량 및 실행력** | ... | ... |
            
            ### 5. Master Action Plan
            - **전략적 네트워킹 및 멘토링 세션 참여**: ...
            - **실무 성과 가속화를 위한 몰입형 프로젝트 설계**: ...
            - **인문학 및 고전 교육 이수**: ...
            """
            
            user_prompt = f"- 이름: {name}\n- 생년월일: {birth}\n- 성별: {gender}\n- 혈액형: {blood_type}\n- 별자리: {zodiac}\n- MBTI: {mbti}\n- 직업(전공): {job}\n- 세부 성향 점수 분포: {enneagram_text}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.4,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )
            
            report_content = response.choices[0].message.content
            
            st.success("✅ 전문 심층 분석 리포트가 성공적으로 생성되었습니다.")
            
            with st.container():
                st.markdown("<div class='report-container'>", unsafe_allow_html=True)
                st.plotly_chart(create_radar_chart(enneagram_scores), use_container_width=True)
                st.markdown("---")
                st.markdown(report_content)
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("")
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button("📄 텍스트 리포트 (.txt)", data=report_content, file_name=f"{name}_Executive_Report.txt", mime="text/plain", use_container_width=True)
            with col_dl2:
                pdf_file = create_pdf(report_content, name)
                with open(pdf_file, "rb") as f:
                    st.download_button("📕 브로슈어형 PDF 리포트 (.pdf)", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
