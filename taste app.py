import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="커리어 및 회복탄력성 심층 분석 리포트", page_icon="🌟", layout="centered")

st.title("🌟 커리어 발전 및 회복탄력성 심층 분석 리포트")
st.write("전문적인 성향 데이터와 직업선호도(L형) 검사를 기반으로, 커리어 성공 전략뿐만 아니라 마음의 회복탄력성과 인품 성장의 길을 제시합니다.")

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
    
    submitted = st.form_submit_button("커리어 & 회복탄력성 심층 리포트 생성하기", use_container_width=True)

# 3. PDF 생성 함수
def create_pdf(text, user_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    
    lines = text.split('\n')
    for line in lines:
        clean_line = line.replace('#', '').replace('*', '').strip()
        if clean_line:
            pdf.multi_cell(0, 7, clean_line.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(1.5)
            
    filename = f"{user_name}_커리어_회복탄력성_리포트.pdf"
    pdf.output(filename)
    return filename

# 4. 방사형 차트 생성 함수
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
                line_color='#3A86FF',
                fillcolor='rgba(58, 134, 255, 0.3)'
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
        with st.spinner("커리어 역량, 회복탄력성, 인품 및 성품 성장을 정밀 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            # AI 프롬프트 (커리어 + 회복탄력성 + 인품향상 중심, 명칭 노출 금지, 개조식 및 표 활용)
            system_prompt = """
            # ROLE: 최고 수준의 수석 커리어 코치 및 멘탈/인성 리더십 컨설턴트
            # RULES (CRITICAL):
            1. '사주', '에니어그램', '별자리', '혈액형'이라는 기법명 단어를 본문에 절대 직접 언급하지 말 것. 대신 타고난 기질, 내면의 심리적 동기, 고유의 성향적 특징으로 표현할 것.
            2. 리포트의 핵심 초점을 다음 3가지 영역에 강력하게 맞출 것:
               - **[커리어 성장]**: 직업선호도(L형) 검사 체계(홀랜드 6유형 및 성격 5요인)를 반영한 직무 강점 및 커리어 로드맵.
               - **[회복탄력성(Resilience)]**: 역경, 스트레스, 번아웃 상황에서 다시 일어설 수 있는 내면의 힘과 마음 챙김 전략.
               - **[인품 및 리더십 향상]**: 대인관계에서 신뢰를 얻고, 타인을 포용하며 성숙한 인품으로 거듭나기 위한 내면 성찰 과제.
            3. 길고 지루한 서술식 문장을 최소화하고, **개조식 불렛포인트**와 **핵심 요약 표(Markdown Table)**를 적극 활용하여 가독성을 극대화할 것.
            4. 통찰력 있고 따뜻하면서도 실천 가능한 구체적 조언을 담을 것.
            
            # OUTPUT FORMAT (마크다운 구조 엄수):
            ## 🌟 [이름] 님 커리어 및 회복탄력성 심층 분석 리포트
            
            ### 1. 🔍 타고난 본질 및 내면의 심리 동기 분석
            - (기질적 강점과 에너지의 원천 분석)
            
            ### 2. 💼 직업선호도 기반 커리어 로드맵 및 직무 역량
            - (직업/전공과 연계한 핵심 직무 경쟁력 분석)
            
            ### 3. 🌱 역경 극복을 위한 회복탄력성(Resilience) 진단
            - (스트레스 취약점 및 마음 근육을 단단하게 만드는 실천법)
            
            ### 4. 🤝 성숙한 인품과 관계 형성을 위한 리더십 가이드
            - (타인과의 소통 방식 성찰 및 덕망 있는 인품 향상 솔루션)
            
            | 분석 영역 | 핵심 진단 결과 | 실천적 성장 솔루션 |
            | :--- | :--- | :--- |
            | **커리어 및 성취** | ... | ... |
            | **마음 근육 (회복력)** | ... | ... |
            | **인품 및 대인관계** | ... | ... |
            
            ### 5. 🚀 일상의 성장을 위한 Master Action Plan
            - (단기/장기 삶의 밸런스 유지 전략)
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
            
            # 성향 방사형 차트 시각화
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
                    file_name=f"{name}_커리어_회복탄력성_리포트.txt",
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
