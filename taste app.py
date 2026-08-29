import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="다차원 성향 분석 리포트", page_icon="🔮", layout="centered")

st.title("🔮 다차원 성향 분석 리포트")
st.write("다양한 차원의 데이터를 종합하여 입체적인 분석 결과와 도표를 제공합니다.")

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.subheader("기본 정보")
    
    # 기본 정보 1열
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        name = st.text_input("이름", placeholder="예: 홍길동")
    with col2:
        birth = st.date_input(
            "생년월일 (사주 분석용)",
            min_value=datetime.date(1930, 1, 1),
            max_value=datetime.date(2026, 12, 31),
            value=datetime.date(1990, 1, 1)
        )
    with col3:
        gender = st.radio("성별", ["남성", "여성", "선택 안함"])
        
    # 기본 정보 2열
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        blood_type = st.selectbox("혈액형", ["A형", "B형", "O형", "AB형"])
    with col5:
        zodiac = st.text_input("별자리", placeholder="예: 황소자리")
    with col6:
        mbti = st.text_input("MBTI", placeholder="예: INTJ")
    with col7:
        job = st.text_input("직업/전공", placeholder="예: 디자이너")
    
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
    
    # 폼 제출 버튼
    submitted = st.form_submit_button("다차원 분석 리포트 생성하기", use_container_width=True)

# 3. PDF 생성 함수 (텍스트 리포트용)
def create_pdf(text, user_name):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", size=12)
    
    lines = text.split('\n')
    for line in lines:
        clean_line = line.replace('#', '').replace('*', '').strip()
        if clean_line:
            pdf.multi_cell(0, 8, clean_line.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(2)
    
    filename = f"{user_name}_다차원분석_리포트.pdf"
    pdf.output(filename)
    return filename

# 4. 방사형 차트 생성 함수
def create_radar_chart(scores):
    categories = ['1번(완벽)', '2번(조력)', '3번(성취)', '4번(개성)', '5번(탐구)', '6번(충성)', '7번(열정)', '8번(도전)', '9번(평화)']
    # 레이더 차트는 시작점과 끝점이 이어져야 하므로 첫 번째 값을 마지막에 추가
    categories = [*categories, categories[0]]
    plot_scores = [*scores, scores[0]]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=plot_scores,
                theta=categories,
                fill='toself',
                name='에니어그램 프로파일',
                line_color='#FF6B6B',
                fillcolor='rgba(255, 107, 107, 0.4)'
            )
        ]
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 20])),
        showlegend=False,
        title=dict(text="📊 나의 성향 밸런스 도표", font=dict(size=18)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

# 5. AI 호출 및 결과 출력 로직
if submitted:
    if not name:
        st.warning("이름을 입력해주세요.")
    else:
        with st.spinner("사주, 에니어그램, 별자리 등을 융합하여 다차원 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            # AI 프롬프트 (다차원 분석 지시)
            system_prompt = """
            # ROLE: 다차원 운명 및 심리 분석 마스터 (사주 명리, 에니어그램, 점성술, 성격심리 통합 전문가)
            # RULES:
            1. 제공된 생년월일(사주 명리 관점), 에니어그램 점수, 별자리, 혈액형, MBTI, 직업 데이터를 모두 융합하여 하나의 일관된 스토리텔링으로 분석할 것.
            2. 각 차원(사주, 에니어그램, 별자리, 혈액형)이 서로 어떻게 상호작용하고 보완하는지 입체적으로 설명할 것. (예: "사주상 불의 기운이 강한데, 에니어그램 7번 성향과 겹쳐 폭발적인 추진력을 냅니다.")
            3. 긍정적인 잠재력뿐만 아니라, 기질적 결핍이나 주의해야 할 리스크도 함께 분석하여 현실적인 조언을 제공할 것.
            4. 전문가답고 신뢰감 있는 어투를 사용할 것.
            
            # OUTPUT FORMAT:
            ## 🔮 다차원 종합 분석 리포트 ([이름] 님)
            ### 1. 🌟 선천적 기질 및 운명의 흐름 (사주, 별자리, 혈액형 기반)
            ### 2. 🧠 심리 동기 및 행동 패턴 (에니어그램, MBTI 중심)
            ### 3. 💼 직업적 강점 및 사회생활 분석 (현재 직업과 성향의 궁합)
            ### 4. 🚀 인생의 밸런스를 위한 마스터 조언
            """
            
            user_prompt = f"""
            - 이름: {name}
            - 생년월일: {birth}
            - 성별: {gender}
            - 혈액형: {blood_type}
            - 별자리: {zodiac}
            - MBTI: {mbti}
            - 직업(전공): {job}
            - 에니어그램 전체 점수: {enneagram_text}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.5,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            report_content = response.choices[0].message.content
            
            st.success("다차원 리포트 생성이 완료되었습니다!")
            
            # [도표 출력 부분] 에니어그램 방사형 차트 그리기
            st.plotly_chart(create_radar_chart(enneagram_scores), use_container_width=True)
            
            # [리포트 출력 부분] AI 텍스트 리포트
            st.markdown(f"<div style='background-color:#f0f2f6; padding:20px; border-radius:10px;'>{report_content}</div>", unsafe_allow_html=True)
            st.write("")
            
            # 다운로드 버튼
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📄 텍스트(.txt) 다운로드",
                    data=report_content,
                    file_name=f"{name}_다차원_분석_리포트.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_dl2:
                pdf_file = create_pdf(report_content, name)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📕 PDF 텍스트 리포트 다운로드",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf",
                        use_container_width=True
                    )
