import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime
import plotly.graph_objects as go

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="커리어 및 회복탄력성 심층 분석 리포트", page_icon="🌟", layout="centered")

st.title("🌟 커리어 발전 및 회복탄력성 심층 분석 리포트")
st.write("다각도의 성향 데이터와 직업선호도(L형) 검사를 기반으로, 커리어 성공 전략, 마음 근육(회복탄력성), 깊이 있는 인품 성장의 길을 풍성하고 디테일하게 제시합니다.")

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
    
    submitted = st.form_submit_button("풍성한 심층 분석 리포트 생성하기", use_container_width=True)

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
            
    filename = f"{user_name}_풍성한_심층분석_리포트.pdf"
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
                line_color='#7209B7',
                fillcolor='rgba(114, 9, 183, 0.25)'
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
        with st.spinner("방대한 심층 데이터를 바탕으로 풍성하고 입체적인 리포트를 작성 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_scores = [e1, e2, e3, e4, e5, e6, e7, e8, e9]
            enneagram_text = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            # AI 프롬프트 (개조식의 깔끔함을 유지하되, 각 항목마다 풍성한 설명과 디테일을 담도록 지시)
            system_prompt = """
            # ROLE: 수석 커리어 컨설턴트, 심층 심리 분석가 및 인성 리더십 마스터
            # RULES (CRITICAL):
            1. '사주', '에니어그램', '별자리', '혈액형'이라는 기법명 단어를 본문에 절대 직접 언급하지 말 것. 대신 타고난 선천적 기질, 심리적 동기 구조, 내면의 에너지 패턴으로 표현할 것.
            2. **개조식 형식을 엄수하되, 각 항목의 내용을 매우 풍성하고 깊이 있게 작성할 것.** 단순히 단답형으로 끝내지 말고, "왜 그런 성향이 나타나는지(원인)", "업무 및 일상에서 어떻게 드러나는지(현상)", "이를 어떻게 극대화하거나 보완해야 하는지(솔루션)"를 상세히 풀어쓸 것.
            3. 리포트의 핵심 축인 **[커리어 성장]**, **[회복탄력성]**, **[인품 및 리더십]** 영역에서 각 항목당 최소 3~4개의 세부 하위 불렛포인트를 제공하여 정보의 밀도를 극대화할 것.
            4. 직업선호도(L형) 체계(홀랜드 6유형 및 성격 5요인)와 연계하여 실무에서 즉시 활용할 수 있는 구체적인 가이드를 제공할 것.
            
            # OUTPUT FORMAT (마크다운 구조 엄수):
            ## 🌟 [이름] 님 커리어 및 회복탄력성 심층 분석 리포트
            
            ### 1. 🔍 타고난 본질 및 내면의 심리 동기 정밀 해부
            - **에너지의 원천과 행동 동기**: (풍성하고 상세한 설명)
            - **무의식적 방어기제와 스트레스 유발 요인**: (풍성하고 상세한 설명)
            - **타인이 바라보는 첫인상과 실제 내면의 괴리**: (풍성하고 상세한 설명)
            
            ### 2. 💼 직업선호도(L형) 기반 커리어 로드맵 및 핵심 직무 역량
            - **강점 극대화 영역 (주력 직무 매칭)**: (풍성하고 상세한 설명)
            - **잠재적 취약점 및 리스크 관리 전략**: (풍성하고 상세한 설명)
            - **조직 내 협업 및 성과 창출을 위한 무기**: (풍성하고 상세한 설명)
            
            ### 3. 🌱 역경 극복 및 멘탈 강화를 위한 회복탄력성(Resilience) 솔루션
            - **번아웃 및 위기 상황 시 나타나는 심리적 반응 패턴**: (풍성하고 상세한 설명)
            - **감정적 회복 속도를 높이는 나만의 마음 챙김 루틴**: (풍성하고 상세한 설명)
            - **실패를 성장의 자양분으로 전환하는 인지적 유연성 확보 방안**: (풍성하고 상세한 설명)
            
            ### 4. 🤝 성숙한 인품과 덕망 있는 리더십 빌드업 가이드
            - **대인관계 속 신뢰 형성을 위한 소통의 기술**: (풍성하고 상세한 설명)
            - **타인을 포용하고 영향력을 넓히는 품격 있는 태도**: (풍성하고 상세한 설명)
            - **갈등 상황 발생 시 지혜로운 중재 및 해결 역량**: (풍성하고 상세한 설명)
            
            | 분석 영역 | 핵심 진단 결과 (Depth Summary) | 실천적 성장 솔루션 (Action Items) |
            | :--- | :--- | :--- |
            | **커리어 및 성취** | ... | ... |
            | **마음 근육 (회복력)** | ... | ... |
            | **인품 및 대인관계** | ... | ... |
            
            ### 5. 🚀 일상의 성장을 위한 Master Action Plan (단기/장기)
            - **즉시 실천 가능한 단기 과제 (1~3개월)**: (구체적인 실천 행동 3가지 이상)
            - **장기적 커리어 및 인격 완성 로드맵 (1년 이상)**: (지향해야 할 궁극적 방향성)
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
            
            st.success("풍성한 심층 리포트가 성공적으로 생성되었습니다!")
            
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
                    file_name=f"{name}_풍성한_커리어_회복탄력성_리포트.txt",
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
