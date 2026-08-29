import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="종합 성향 분석 리포트", page_icon="📋", layout="centered")

st.title("📋 종합 생애 및 성향 분석 리포트 생성기")
st.write("대상자의 정보를 입력하시면 AI가 종합 분석 리포트를 즉시 생성합니다.")

# 2. 사용자 입력 폼
with st.form("user_input_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름", placeholder="예: 주진희")
        birth = st.date_input("생년월일")
        zodiac = st.text_input("별자리", placeholder="예: 황소자리")
    with col2:
        mbti = st.text_input("MBTI", placeholder="예: INTJ")
        enneagram = st.text_input("에니어그램", placeholder="예: 3번 유형 (18점)")
    
    submitted = st.form_submit_button("리포트 생성하기")

# 3. PDF 생성 함수 (한글 폰트 지원 설정 필요)
def create_pdf(text, user_name):
    pdf = FPDF()
    pdf.add_page()
    # 기본 폰트 설정 (영문/기호 지원)
    pdf.set_font("Helvetica", size=12)
    
    # 텍스트 줄바꿈 처리 및 PDF 출력
    lines = text.split('\n')
    for line in lines:
        # UTF-8 한글 출력을 위해 encode/decode 지원 또는 외부 한글 폰트(NanumGothic) 추가 권장
        clean_line = line.replace('#', '').replace('*', '').strip()
        if clean_line:
            pdf.multi_cell(0, 8, clean_line.encode('latin-1', 'replace').decode('latin-1'))
            pdf.ln(2)
    
    filename = f"{user_name}_분석_리포트.pdf"
    pdf.output(filename)
    return filename

# 4. AI 호출 및 결과 출력
if submitted:
    if not name:
        st.warning("이름을 입력해주세요.")
    else:
        with st.spinner("다차원 성향 데이터를 종합 분석 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 종합 생애 설계 및 심리 분석 전문가
            # RULES:
            1. 사주, 에니어그램, MBTI, 별자리라는 기법명 단어를 본문에 절대 직접 언급하지 말 것.
            2. '회복탄력성(Resilience)' 및 '사회생활/인생 전반'에 가장 높은 가중치를 두고 분석할 것.
            3. 전문 직업검사표처럼 객관적이고 논리적인 어조(~합니다)를 유지할 것.
            # OUTPUT FORMAT:
            ## 종합 생애 및 성향 분석 리포트 ([이름] 님)
            ### 1. 인생 전반의 핵심 동력 및 강점
            ### 2. 사회생활 및 위기 상황에서의 취약점
            ### 3. 회복탄력성 강화 및 삶의 질 향상을 위한 전략
            """
            
            user_prompt = f"""
            - 이름: {name}
            - 생년월일: {birth}
            - 별자리: {zodiac}
            - 에니어그램: {enneagram}
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
            st.markdown("---")
            st.markdown(report_content)
            st.markdown("---")
            
            # 다운로드 버튼 (텍스트 파일 & PDF)
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    label="📄 텍스트(.txt) 파일 다운로드",
                    data=report_content,
                    file_name=f"{name}_성향_분석_리포트.txt",
                    mime="text/plain"
                )
            with col_dl2:
                # PDF 파일 생성 및 다운로드
                pdf_file = create_pdf(report_content, name)
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📕 PDF 리포트 다운로드",
                        data=f,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )