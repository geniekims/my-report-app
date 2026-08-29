import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="인문학 기반 커리어 및 회복탄력성 리포트", page_icon="🏛️", layout="centered")

st.title("🏛️ 인문학 기반 커리어 및 회복탄력성 심층 분석 리포트")
st.write("다각도의 성향 데이터와 고전 인문학적 통찰을 융합하여, 커리어 성공 전략, 회복탄력성, 성숙한 인품 성장을 위한 맞춤형 지침을 제공합니다.")

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
    
    submitted = st.form_submit_button("인문학 처방 심층 리포트 생성하기", use_container_width=True)

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
            
    filename = f"{user_name}_인문학_처방_심층분석_리포트.pdf"
    pdf.output(filename)
    return filename

# 4. 방사형 차트 생성 함수 (에니어그램)
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

# 5. 핵심 역량 바 차트 생성 함수 (시각 도표 추가)
def create_bar_chart():
    categories = ['커리어 전문성', '회복탄력성(멘탈)', '인품 및 리더십', '인문학적 통찰']
    values = [85, 78, 82, 90]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=['#2A9D8F', '#E76F51', '#F4A261', '#457B9D'],
                text=values,
                textposition='auto'
            )
        ]
    )
    fig.update_layout(
        title=dict(text="📊 주요 성장 잠재력 및 역량 진단 지수", font=dict(size=18)),
        yaxis=dict(range=[0, 100], title="점수 (100점 만점)"),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

# 6. AI 호출 및 결과 출력 로직
if submitted:
    if not name:
        st.warning("이름을 입력해주세요.")
    else:
        with st.spinner("인문학적 고전 처방 및 다차원 심층 데이터를 정밀 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            # AI 프롬프트 (심플한 제목, 풍성한 내용, 인문학/고전 교육 중심 마스터 액션 플랜)
            system_prompt = """
            # ROLE: 수석 인문학 멘토, 커리어 컨설턴트 및 심층 심리 분석가
            # RULES (CRITICAL):
            1. '사주', '에니어그램', '별자리', '혈액형'이라는 기법명 단어를 본문에 절대 직접 언급하지 말 것. 대신 타고난 선천적 기질, 심리적 동기 구조, 내면의 에너지 패턴으로 표현할 것.
            2. 각 섹션의 대제목은 요구된 대로 **매우 심플하게** 작성할 것 (예: "심리 동기 분석", "커리어 로드맵", "회복탄력성 솔루션", "인품 향상 가이드", "Master Action Plan").
            3. 개조식 불렛포인트 형식을 엄수하되, 각 항목마다 풍성하고 깊이 있는 설명(원인, 현상, 솔루션)을 제공할 것.
            4. **마스터 액션 플랜(Master Action Plan) 및 전반적인 솔루션의 핵심 축을 반드시 '인문학 및 고전(동서양 철학, 역사, 문학 등)에 대한 학습과 교육'에 맞출 것.** 삶의 근본적인 지혜와 멘탈 강화를 위해 고전 읽기와 인문학 교육이 왜 필수적인지 설득력 있게 제안할 것.
            5. 직업선호도(L형) 체계와 연계하여 실무와 인격 수양에 즉시 적용할 수 있는 구체적인 가이드를 담을 것.
            
            # OUTPUT FORMAT (마크다운 구조 엄수):
            ## 🌟 [이름] 님 커리어 및 인문학 심층 분석 리포트
            
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
            - **고전 인문학을 통한 내면 근육 강화법**: (풍성하고 상세한 설명)
            - **실패를 성장의 자양분으로 바꾸는 통찰력**: (풍성하고 상세한 설명)
            
            ### 4. 인품 향상 가이드
            - **대인관계 속 신뢰 형성과 소통의 지혜**: (풍성하고 상세한 설명)
            - **타인을 포용하는 덕망 있는 태도**: (풍성하고 상세한 설명)
            - **인문학적 사유를 통한 인격 완성**: (풍성하고 상세한 설명)
            
            | 분석 영역 | 핵심 진단 결과 (Depth Summary) | 인문학적 처방 솔루션 (Prescription) |
            | :--- | :--- | :--- |
            | **커리어 및 성취** | ... | ... |
            | **마음 근육 (회복력)** | ... | ... |
            | **인품 및 대인관계** | ... | ... |
            
            ### 5. Master Action Plan
            - **인문학 및 고전 교육 이수 계획 (핵심 제안)**: (동서양 고전 독서, 인문학 강좌 수강 등 구체적 실행 방안 3가지 이상 상세 기술)
            - **단기 및 장기 삶의 밸런스 유지 전략**: (지향해야 할 궁극적 방향성)
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
            
            st.success("인문학 처방 리포트가 성공적으로 생성되었습니다!")
            
            # 시각 도표 1: 에니어그램 방사형 차트
            st.plotly_chart(create_radar_chart(enneagram_scores), use_container_width=True)
            
            # 시각 도표 2: 핵심 역량 막대 차트 (추가된 시각 도표)
            st.plotly_chart(create_bar_chart(), use_container_width=True)
            
            # 리포트 본문 출력
            st.markdown(f"<div style='background-color:#f8f9fa; padding:25px; border-radius:12px; border:1px solid #e9ecef;'>{report_content}</div>", unsafe_allow_html=True)
            st.write("")
            
            # 다운로드 버튼
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📄 텍스트(.txt) 다운로드",
                    data=report_content,
                    file_name=f"{name}_인문학처방_리포트.txt",
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
