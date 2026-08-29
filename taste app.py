import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="종합 성향 분석 리포트", page_icon="📋", layout="centered")

st.title("📋 종합 생애 및 성향 분석 리포트 생성기")
st.write("대상자의 정보를 세밀하게 입력하시면 AI가 심층 분석 리포트를 즉시 생성합니다.")

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    st.subheader("기본 정보")
    
    # 기본 정보 1열 (이름, 생년월일, 성별)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        name = st.text_input("이름", placeholder="예: 홍길동")
    with col2:
        birth = st.date_input(
            "생년월일",
            min_value=datetime.date(1960, 1, 1),
            max_value=datetime.date(2026, 12, 31),
            value=datetime.date(1990, 1, 1)
        )
    with col3:
        gender = st.radio("성별", ["남성", "여성", "선택 안함"])
        
    # 기본 정보 2열 (직업, MBTI, 별자리)
    col4, col5, col6 = st.columns(3)
    with col4:
        job = st.text_input("현재 직업 (또는 전공)", placeholder="예: 데이터 분석가")
    with col5:
        mbti = st.text_input("MBTI", placeholder="예: INTJ")
    with col6:
        zodiac = st.text_input("별자리", placeholder="예: 황소자리")
    
    st.markdown("---")
    
    # 에니어그램 9개 유형 점수 입력란 (3x3 그리드 배치)
    st.subheader("에니어그램 유형별 점수 (최대 20점)")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    with col_e1:
        e1 = st.number_input("1번 (완벽주의자)", min_value=0, max_value=20, value=0)
        e4 = st.number_input("4번 (개인주의자)", min_value=0, max_value=20, value=0)
        e7 = st.number_input("7번 (열정적인 사람)", min_value=0, max_value=20, value=0)
        
    with col_e2:
        e2 = st.number_input("2번 (돕고자 하는 사람)", min_value=0, max_value=20, value=0)
        e5 = st.number_input("5번 (탐구자)", min_value=0, max_value=20, value=0)
        e8 = st.number_input("8번 (도전하는 사람)", min_value=0, max_value=20, value=0)
        
    with col_e3:
        e3 = st.number_input("3번 (성취하는 사람)", min_value=0, max_value=20, value=0)
        e6 = st.number_input("6번 (충실한 사람)", min_value=0, max_value=20, value=0)
        e9 = st.number_input("9번 (평화주의자)", min_value=0, max_value=20, value=0)
    
    # 폼 제출 버튼
    submitted = st.form_submit_button("심층 리포트 생성하기", use_container_width=True)

# 3. PDF 생성 함수
def create_pdf(text, user_name):
    pdf = FPDF()
    pdf.add_page()
    
    # 한글 폰트 적용 시 아래 주석 해제 및 프로젝트 폴더에 폰트 파일 삽입
    # pdf.add_font('NanumGothic', '', 'NanumGothic.ttf', uni=True)
    # pdf.set_font('NanumGothic', '', 12)
    
    pdf.set_font("Helvetica", size=12)
    
    lines = text.split('\n')
    for line in lines:
        clean_line = line.replace('#', '').replace('*', '').strip()
        if clean_line:
            pdf.multi_cell(0, 8, clean_line.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(2)
    
    filename = f"{user_name}_분석_리포트.pdf"
    pdf.output(filename)
    return filename

# 4. AI 호출 및 결과 출력 로직
if submitted:
    if not name:
        st.warning("이름을 입력해주세요.")
    else:
        with st.spinner("다차원 성향 데이터를 종합 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            enneagram_data = (
                f"1번({e1}점), 2번({e2}점), 3번({e3}점), 4번({e4}점), 5번({e5}점), "
                f"6번({e6}점), 7번({e7}점), 8번({e8}점), 9번({e9}점)"
            )
            
            system_prompt = """
            # ROLE: 종합 생애 설계 및 심리 분석 전문가
            # RULES:
            1. 사주, 에니어그램, MBTI, 별자리라는 기법명 단어를 본문에 절대 직접 언급하지 말 것.
            2. '회복탄력성(Resilience)' 및 '사회생활/인생 전반'에 가장 높은 가중치를 두고 분석할 것.
            3. 전문 직업검사표처럼 객관적이고 논리적인 어조(~합니다, ~필요가 있습니다)를 유지할 것.
            4. 사용자가 제공한 9가지 성향 점수 분포를 바탕으로, 가장 높은 성향의 장점뿐만 아니라 낮은 점수로 인한 결핍이나 스트레스 상황에서의 방어기제까지 입체적으로 분석할 것.
            5. 사용자가 제공한 직업(또는 전공) 정보와 성향을 결합하여 분석에 반영할 것.
            
            # OUTPUT FORMAT:
            ## 종합 생애 및 성향 분석 리포트 ([이름] 님)
            ### 1. 인생 전반의 핵심 동력 및 강점
            ### 2. 사회생활 및 위기 상황에서의 취약점
            ### 3. 회복탄력성 강화 및 삶의 질 향상을 위한 전략
            """
            
            user_prompt = f"""
            - 이름: {name}
            - 생년월일: {birth}
            - 성별: {gender}
            - 직업(또는 전공): {job}
            - 별자리: {zodiac}
            - 에니어그램 전체 점수 분포 (최대 20점): {enneagram_data}
            - MBTI: {mbti}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            report_content = response.choices[0].message.content
            
            # 화면에 결과 텍스트 출력
            st.success("리포트 생성이 완료되었습니다!")
            st.markdown(f"<div style='background-color:#f0f2f6; padding:20px; border-radius:10px;'>{report_content}</div>", unsafe_allow_html=True)
            st.write("")
            
            # 다운로드 버튼
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📄 텍스트(.txt) 다운로드",
                    data=report_content,
                    file_name=f"{name}_성향_분석_리포트.txt",
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
