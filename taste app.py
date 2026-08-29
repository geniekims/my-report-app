import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="커리어 및 회복탄력성 심층 분석 리포트", page_icon="🧭", layout="centered")

st.title("🧭 개인 맞춤형 커리어 및 회복탄력성 심층 분석 리포트")
st.write("다각도의 성향 데이터와 내면의 심층 통찰을 융합하여, 커리어 성공 전략, 회복탄력성, 성숙한 개인역량 성장을 위한 맞춤형 지침을 제공합니다.")

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.subheader("기본 정보")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        name = st.text_input("이름", placeholder="예: 홍길동")
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
        job = st.text_input("직업/전공", placeholder="예: 기획자")
    
    st.markdown("---")
    
    # 에니어그램 9개 유형 점수 입력란
    st.subheader("에니어그램 유형별 점수 (최대 20점)")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        e1 = st.number_input("1번 (완벽주의자)", min_value=0, max_value=20, value=0)
        e4 = st.number_input("4번 (개인주의자)", min_value=0, max_value=20, value=0)
        e7 = st.number_input("7번 (열정적인 사람)", min_value=0, max_value=20, value=0)
        
    with col_e2:
        e2 = st.number_input("2번 (조력자)", min_value=0, max_value=20, value=0)
        e5 = st.number_input("5번 (탐구자)", min_value=0, max_value=20, value=0)
        e8 = st.number_input("8번 (도전하는 사람)", min_value=0, max_value=20, value=0)
        
    with col_e3:
        e3 = st.number_input("3번 (성취하는 사람)", min_value=0, max_value=20, value=0)
        e6 = st.number_input("6번 (충실한 사람)", min_value=0, max_value=20, value=0)
        e9 = st.number_input("9번 (평화주의자)", min_value=0, max_value=20, value=0)
    
    submitted = st.form_submit_button("심층 리포트 생성하기", use_container_width=True)

# 3. PDF 생성 함수
def create_pdf(text, user_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    
    lines = text.split('\n')
    for line in lines:
        clean_line = line.replace('#', '').replace('*', '').strip()
        if clean_line:
            pdf.multi_cell(0, 6, clean_line.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(1)
            
    filename = f"{user_name}_맞춤형_심층분석_리포트.pdf"
    pdf.output(filename)
    return filename

# 4. 방사형 차트 생성 함수 (기존 스타일 유지)
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
                name='성향 프로파일',
                line_color='#2A9D8F',
                fillcolor='rgba(42, 157, 143, 0.25)'
            )
        ]
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 20])),
        showlegend=False,
        title=dict(text="📊 내면 심리 동기 및 성향 밸런스 도표", font=dict(size=18)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

# 5. AI 호출 및 결과 출력 로직
if submitted:
    if not name:
        st.warning("이름을 입력해주세요.")
    else:
        with st.spinner("다차원 심층 데이터와 고유 성향 프로파일을 정밀 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            # AI 프롬프트 (본문에서는 인문학 배제, Master Action Plan에서만 인문학/고전 교육 + 논리적 이유 + 3가지 세부 액션, 인품->개인역량 변경)
            system_prompt = """
            # ROLE: 수석 커리어 컨설턴트 및 심층 심리 분석가
            # RULES (CRITICAL):
            1. '사주', '에니어그램', '별자리', '혈액형'이라는 기법명 단어를 본문에 절대 직접 언급하지 말 것. 대신 타고난 선천적 기질, 심리적 동기 구조, 내면의 에너지 패턴으로 표현할 것.
            2. **'인문학' 또는 '고전'이라는 단어는 1번~4번 섹션 및 표(Table) 안에서는 절대 사용하지 말 것.** 본문에서는 '내면 성찰', '철학적 사유', '본질적 통찰', '역량 확장' 등의 세련된 표현을 사용할 것.
            3. **오직 마지막 'Master Action Plan' 섹션에서만 인문학 및 고전 교육 처방을 다룰 것.**
               - '핵심제안'이라는 표현은 절대 사용하지 말고 바로 항목명으로 시작할 것.
               - 왜 인문학 및 고전 교육을 추천하는지 그 **타당한 논리적 이유와 근거**를 명확히 서술할 것.
               - 추가적인 액션 2가지를 더 포함하여 **총 3가지의 구체적 실행 액션**(예: 1. 인문학 및 고전 고유 독서·교육 이수, 2. 전략적 네트워킹 및 멘토링 세션 참여, 3. 실무 성과 가속화를 위한 몰입형 프로젝트 설계)을 제시할 것.
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
            - **인문학 및 고전 교육 이수**: (추천하는 논리적 이유와 근거를 포함하여, 동서양 고전 독서 및 심화 강좌 수강 등 구체적 실행 방안 상세 기술)
            - **전략적 네트워킹 및 멘토링 세션 참여**: (개인역량 확장을 위한 외부 전문가 교류 및 피드백 수렴 방안 상세 기술)
            - **실무 성과 가속화를 위한 몰입형 프로젝트 설계**: (단기 및 장기 목표 달성을 위한 자기주도적 성과 도출 로직 상세 기술)
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
            
            st.success("심층 리포트가 성공적으로 생성되었습니다!")
            
            # 시각 도표 출력 (방사형 차트)
            st.plotly_chart(create_radar_chart(enneagram_scores), use_container_width=True)
            
            # 리포트 본문 출력
            st.markdown(f"<div style='background-color:#f8f9fa; padding:25px; border-radius:12px; border:1px solid #e9ecef;'>{report_content}</div>", unsafe_allow_html=True)
            st.write("")
            
            # 다운로드 버튼
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📄 텍스트(.txt) 다운로드",
                    data=report_content,
                    file_name=f"{name}_심층분석_리포트.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_dl2:
                pdf_file = create_pdf(report_content, name)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📕 PDF 리포트 다운로드",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf",
                        use_container_width=True
                    )
