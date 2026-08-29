import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="종합 성향 및 진로 심층 분석 리포트", page_icon="📋", layout="centered")

st.title("📋 종합 성향 및 진로 심층 분석 리포트")
st.write("다양한 성향 데이터와 직업선호도(L형) 검사 결과를 바탕으로 가독성 높은 맞춤형 분석 리포트를 생성합니다.")

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
        job = st.text_input("직업/전공", placeholder="예: 마케터")
    
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
    
    submitted = st.form_submit_button("심층 진로 분석 리포트 생성하기", use_container_width=True)

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
            
    filename = f"{user_name}_진로심층분석_리포트.pdf"
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
                line_color='#2A9D8F',
                fillcolor='rgba(42, 157, 143, 0.3)'
            )
        ]
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 20])),
        showlegend=False,
        title=dict(text="📊 에니어그램 성향 밸런스 도표", font=dict(size=18)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

# 5. AI 호출 및 결과 출력 로직
if submitted:
    if not name:
        st.warning("이름을 입력해주세요.")
    else:
        with st.spinner("직업선호도(L형) 및 심층 기질 데이터를 정밀 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            # AI 프롬프트 (명칭 노출 금지 및 직업선호도 L형, 개조식/표 구조 강화)
            system_prompt = """
            # ROLE: 최고 수준의 진로 심리 상담 전문가 및 수석 커리어 코치
            # RULES (CRITICAL):
            1. '사주', '에니어그램', '별자리', '혈액형'이라는 기법명 단어를 본문에 절대 직접 언급하지 말 것. 대신 타고난 기질, 내면의 심리적 동기, 성향적 특징으로 표현할 것.
            2. 첨부된 '직업선호도 검사(L형) 결과지'의 체계(홀랜드 흥미 6유형: 현실형, 탐구형, 예술형, 사회형, 진취형, 관습형 / 성격 5요인: 외향성, 호감성, 성실성, 정서적 안정성, 개방성 / 생활사 9개 요인: 대인관계, 독립심, 야망 등)를 차용하여 아주 길고 깊이 있게 분석할 것.
            3. 모든 분석 항목은 길고 장황한 산문 대신 **개조식 불렛포인트**와 **핵심 요약 표(Markdown Table)**를 적극 활용하여 가독성이 매우 높게 구성할 것.
            4. 각 항목별로 구체적인 예시와 실천 가능한 맞춤형 조언을 풍부하게 작성할 것.
            
            # OUTPUT FORMAT (마크다운 구조 엄수):
            ## 📋 [이름] 님 종합 성향 및 진로 심층 분석 리포트
            
            ### 1. 🔍 핵심 기질 및 심층 성향 프로파일 (내면 동기 분석)
            - (개조식 항목들로 깊이 있게 분석)
            
            ### 2. 🎯 직업 흥미 및 행동 패턴 정밀 진단 (L형 검사 기반)
            - (홀랜드 유형 및 강점 영역 분석)
            
            | 분석 영역 | 주요 특징 및 수준 | 업무 환경 적합도 |
            | :--- | :--- | :--- |
            | **대인관계 및 협업** | ... | ... |
            | **성실성 및 책임감** | ... | ... |
            | **도전 정신 및 야망** | ... | ... |
            
            ### 3. 💼 맞춤형 직무 역량 및 추천 커리어 패스
            - (직업/전공 연계 구체적 직무 제안)
            
            ### 4. 🚀 커리어 도약을 위한 실전 Action Plan
            - (단기/장기 성장 전략 및 주의할 점)
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
            
            st.success("심층 분석 리포트가 성공적으로 생성되었습니다!")
            
            # 에니어그램 방사형 차트 시각화
            st.plotly_chart(create_radar_chart(enneagram_scores), use_container_width=True)
            
            # AI 분석 리포트 본문 출력
            st.markdown(f"<div style='background-color:#f8f9fa; padding:25px; border-radius:12px; border:1px solid #e9ecef;'>{report_content}</div>", unsafe_allow_html=True)
            st.write("")
            
            # 파일 다운로드 버튼
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📄 텍스트(.txt) 다운로드",
                    data=report_content,
                    file_name=f"{name}_심층진로분석_리포트.txt",
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
