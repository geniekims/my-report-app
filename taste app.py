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

# 1. 페이지 기본 설정 및 프로페셔널 CSS 스타일 적용
st.set_page_config(
    page_title="Executive Career & Resilience Intelligence",
    page_icon="💼",
    layout="centered"
)

# 전문적이고 모던한 컨설팅 펌 스타일의 CSS 주입
st.markdown("""
    <style>
    .main {
        background-color: #F8FAFC;
    }
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #0F172A;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .report-container {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #0F172A;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1E293B;
        border-color: #1E293B;
    }
    </style>
""", unsafe_allow_html=True)

# 헤더 영역
st.markdown("<h1 style='text-align: center; color: #0F172A; margin-bottom: 5px;'>💼 Executive Intelligence Report</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1rem; margin-bottom: 30px;'>다차원 심리 동기 구조 및 커리어 성공 전략 통합 진단 플랫폼</p>", unsafe_allow_html=True)

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.markdown("### 👤 진단 대상자 기본 프로필")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        name = st.text_input("성명", placeholder="예: 홍길동")
    with col2:
        birth = st.date_input(
            "생년월일",
            min_value=datetime.date(1930, 1, 1),
            max_value=datetime.date(2026, 12, 31),
            value=datetime.date(1990, 1, 1)
        )
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
    st.markdown("<p style='color: #64748B; font-size: 0.9rem;'>각 영역별 내면 동기 강도를 0~20점 기준으로 입력해주세요.</p>", unsafe_allow_html=True)
    
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
    
    st.markdown("")
    submitted = st.form_submit_button("✨ 전문 심층 분석 리포트 생성", use_container_width=True)

# 3. ReportLab을 이용한 프리미엄 PDF 생성 함수 (전문 디자인 적용)
def create_pdf(text, user_name):
    filename = f"{user_name}_Executive_Intelligence_Report.pdf"
    doc = SimpleDocTemplate(
        filename, 
        pagesize=A4, 
        rightMargin=45, 
        leftMargin=45, 
        topMargin=45, 
        bottomMargin=45
    )
    
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    if not os.path.exists(font_path):
        font_path = "NanumGothic.ttf"
    
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', font_path)) # 동일 폰트 대체
        font_name = 'NanumGothic'
    except:
        font_name = 'Helvetica'
        
    styles = getSampleStyleSheet()
    
    # 전문적 디자인 스타일 정의
    doc_title_style = ParagraphStyle(
        'DocTitle',
        fontName=font_name,
        fontSize=18,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6,
        alignment=1 # 중앙 정렬
    )
    
    doc_subtitle_style = ParagraphStyle(
        'DocSubTitle',
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=20,
        alignment=1
    )
    
    h_style = ParagraphStyle(
        'ReportHeader',
        fontName=font_name,
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        fontName=font_name,
        fontSize=9.5,
        leading=15,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    story = []
    
    # 문서 헤더 장식
    story.append(Paragraph(f"<b>EXECUTIVE INTELLIGENCE ASSESSMENT</b>", doc_subtitle_style))
    story.append(Paragraph(f"<b>{user_name} 님 맞춤형 심층 커리어 & 리더십 리포트</b>", doc_title_style))
    story.append(Spacer(1, 10))
    
    # 구분선 스타일 테이블 활용
    divider = Table([['']], colWidths=[500], rowHeights=[2])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            story.append(Spacer(1, 10))
            story.append(Paragraph(line[3:], h_style))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], h_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {line[2:]}", body_style))
        elif line.startswith('|'):
            if '---' in line:
                continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            if len(cols) >= 3:
                story.append(Paragraph(f"<b>[{cols[0]}]</b> {cols[1]} <br/><font color='#64748B'>💡 Solution: {cols[2]}</font>", body_style))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(line, body_style))
            
    doc.build(story)
    return filename

# 4. 방사형 차트 생성 함수 (컨설팅 대시보드 스타일)
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
                line_color='#0F172A',
                fillcolor='rgba(15, 23, 42, 0.12)'
            )
        ]
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 20], color="#94A3B8"),
            angularaxis=dict(color="#334155")
        ),
        showlegend=False,
        title=dict(text="📊 다차원 내면 동기 및 성향 밸런스 매트릭스", font=dict(size=16, color="#0F172A")),
        margin=dict(l=50, r=50, t=60, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# 5. AI 호출 및 결과 출력 로직
if submitted:
    if not name:
        st.warning("진단 대상자의 성명을 입력해주세요.")
    else:
        with st.spinner("전문 컨설팅 엔진이 다차원 데이터를 정밀 분석 및 시각화 리포트를 구성하고 있습니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            system_prompt = """
            # ROLE: 글로벌 최고 수준의 수석 커리어 컨설턴트 및 조직 심리 전략가
            # RULES (CRITICAL):
            1. '사주', '에니어그램', '별자리', '혈액형'이라는 기법명 단어를 본문에 절대 직접 언급하지 말 것. 대신 타고난 선천적 기질, 심리적 동기 구조, 내면의 에너지 패턴으로 표현할 것.
            2. **'인문학' 또는 '고전'이라는 단어는 1번~4번 섹션 및 표(Table) 안에서는 절대 사용하지 말 것.** 본문에서는 '내면 성찰', '철학적 사유', '본질적 통찰', '역량 확장' 등의 세련된 표현을 사용할 것.
            3. **오직 마지막 'Master Action Plan' 섹션에서만 3가지 실행 액션을 제시할 것.**
               - '핵심제안'이라는 표현은 절대 사용하지 말 것.
               - 1번째 액션: **전략적 네트워킹 및 멘토링 세션 참여** (외부 교류 및 피드백 수렴)
               - 2번째 액션: **실무 성과 가속화를 위한 몰입형 프로젝트 설계** (자기주도적 성과 도출 로직)
               - 3번째 액션: **인문학 및 고전 교육 이수** (왜 이 교육이 앞선 두 가지 액션과 멘탈 강화의 근본적인 완성형 처방이 되는지 타당한 논리적 이유와 근거를 포함하여 상세 기술)
            4. 기존 '인품 향상 가이드' 및 관련 항목들은 전부 **'개인역량 향상 가이드'**로 변경하여 개인의 실무적 능력, 문제해결력, 성과 창출력 중심의 내용을 전개할 것.
            5. 각 섹션의 대제목은 요구된 대로 **매우 심플하게** 작성할 것 (예: "심리 동기 분석", "커리어 로드맵", "회복탄력성 솔루션", "개인역량 향상 가이드", "Master Action Plan").
            6. 개조식 불렛포인트 형식을 엄수하되, 각 항목마다 풍성하고 깊이 있는 설명을 제공할 것.
            
            # OUTPUT FORMAT (마크다운 구조 엄수):
            ## 🌟 [이름] 님 맞춤형 심층 분석 리포트
            
            ### 1. 심리 동기 분석
            - **에너지의 원천과 행동 동기**: (풍성하고 상세한 설명)
            - **무의식적 방어기제와 스트레스 유발 요인**: (풍성하고 상세한 설명)
            - **내면의 고유한 성향적 특징**: (풍성하고 상세한 설명)
            
            ### 2. 커리어 로드맵
            - **강점 극대화 영역 (주력 직무 매칭)**: (풍성하고 상세한 설명)
            - **잠재적 리스크 관리 전략**: (풍성하고 상세한 설명)
            - **조직 내 성과 창출을 위한 핵심 무기**: (풍성하고 상세한 설명)
            
            ### 3. 회복탄력성 솔루션
            - **번아웃 및 위기 시 심리적 반응 패턴**: (풍성하고 상세한 설명)
            - **내면 근육 강화 및 위기 대처법**: (풍성하고 상세한 설명)
            - **실패를 성장의 자양분으로 바꾸는 통찰력**: (풍성하고 상세한 설명)
            
            ### 4. 개인역량 향상 가이드
            - **직무 전문성 심화와 실행력 강화**: (풍성하고 상세한 설명)
            - **복잡한 문제 해결 및 전략적 사고**: (풍성하고 상세한 설명)
            - **균형 잡힌 사유를 통한 성과 확장**: (풍성하고 상세한 설명)
            
            | 분석 영역 | 핵심 진단 결과 (Depth Summary) | 맞춤형 성장 솔루션 (Prescription) |
            | :--- | :--- | :--- |
            | **커리어 및 성취** | ... | ... |
            | **마음 근육 (회복력)** | ... | ... |
            | **개인역량 및 실행력** | ... | ... |
            
            ### 5. Master Action Plan
            - **전략적 네트워킹 및 멘토링 세션 참여**: (개인역량 확장을 위한 외부 전문가 교류 및 피드백 수렴 방안 상세 기술)
            - **실무 성과 가속화를 위한 몰입형 프로젝트 설계**: (단기 및 장기 목표 달성을 위한 자기주도적 성과 도출 로직 상세 기술)
            - **인문학 및 고전 교육 이수**: (앞선 역량 확장과 실행력을 단단하게 지탱해 줄 근본적 통찰과 멘탈 강화를 위해, 동서양 고전 독서 및 심화 강좌 수강이 왜 필수적인지 그 논리적 이유와 구체적 실행 방안 상세 기술)
            """
            
            user_prompt = f"""
            - 이름: {name}
            - 생년월일: {birth}
            - 성별: {gender}
            - 혈액형: {blood_type}
            - 별자리: {zodiac}
            - MBTI: {mbti}
            - 직업(전공): {job}
            - 세부 성향 점수 분포: {enneagram_text}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.4,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            report_content = response.choices[0].message.content
            
            st.success("✅ 전문 심층 분석 리포트가 성공적으로 생성되었습니다.")
            
            # 결과물 컨테이너 감싸기
            with st.container():
                st.markdown("<div class='report-container'>", unsafe_allow_html=True)
                
                # 방사형 차트 시각화
                st.plotly_chart(create_radar_chart(enneagram_scores), use_container_width=True)
                st.markdown("---")
                
                # 리포트 본문 출력
                st.markdown(report_content)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("")
            st.markdown("### 📥 공식 문서 다운로드")
            
            # 다운로드 버튼 레이아웃
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📄 텍스트 리포트 (.txt)",
                    data=report_content,
                    file_name=f"{name}_Executive_Report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_dl2:
                pdf_file = create_pdf(report_content, name)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📕 프리미엄 PDF 리포트 (.pdf)",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf",
                        use_container_width=True
                    )
