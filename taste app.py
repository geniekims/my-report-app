import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import datetime
import re

# 1. 페이지 설정 및 프리미엄 UI 스타일
st.set_page_config(page_title="Executive Intelligence Report", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F1F5F9; }
    h1, h2, h3 { color: #0F172A; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white; border-radius: 6px; font-weight: 600; border: none; 
        padding: 0.7rem 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #1E40AF 0%, #2563EB 100%);
        box-shadow: 0 6px 8px -1px rgba(0,0,0,0.15);
    }
    .report-box {
        background-color: white; padding: 40px; border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -4px rgba(0,0,0,0.05);
        margin-top: 20px; border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); padding: 30px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h1 style='color: white; margin-bottom: 10px; font-size: 28px;'>Executive Intelligence Report</h1>
        <p style='color: #94A3B8; font-size: 15px; margin: 0;'>다차원 심리 기질 및 역량 진단 전문 프리미엄 분석 솔루션</p>
    </div>
""", unsafe_allow_html=True)

# 2. 사용자 입력 폼 (기존 폼 형태 유지)
with st.form("user_input_form"):
    st.markdown("### 👤 기본 프로필 및 심리 성향 진단")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: 
        name = st.text_input("성명", value="홍길동", placeholder="예: 홍길동")
    with col2: 
        birth = st.date_input(
            "생년월일", 
            value=datetime.date(2000, 1, 1), 
            min_value=datetime.date(1950, 1, 1), 
            max_value=datetime.date.today()
        )
    with col3: 
        blood_type = st.selectbox("혈액형", ["A형", "B형", "O형", "AB형"])
    
    mbti_list = [
        "ISTJ", "ISFJ", "INFJ", "INTJ", 
        "ISTP", "ISFP", "INFP", "INTP", 
        "ESTP", "ESFP", "ENFP", "ENTP", 
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]
    with col4: 
        mbti = st.selectbox("MBTI", mbti_list)
    with col5: 
        job = st.text_input("직무 / 전공", value="생산직", placeholder="예: 생산직")
    
    st.markdown("---")
    st.markdown("### 📊 다차원 내면 동기 척도 (0~20점)")
    st.caption("※ 성격 5요인 및 직무 핵심 역량 지표는 입력된 프로필과 내면 동기 척도를 기반으로 AI가 자동 유추·도출합니다.")
    
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        e1 = st.number_input("완벽성 및 원칙 지향", 0, 20, 15)
        e4 = st.number_input("독창성 및 표현 지향", 0, 20, 12)
        e7 = st.number_input("열정 및 비전 지향", 0, 20, 10)
    with col_e2:
        e2 = st.number_input("조력 및 공감 지향", 0, 20, 14)
        e5 = st.number_input("탐구 및 분석 지향", 0, 20, 18)
        e8 = st.number_input("도전 및 결단 지향", 0, 20, 11)
    with col_e3:
        e3 = st.number_input("성취 및 목표 지향", 0, 20, 16)
        e6 = st.number_input("책임 및 안정 지향", 0, 20, 13)
        e9 = st.number_input("조화 및 수용 지향", 0, 20, 9)

    submitted = st.form_submit_button("프리미엄 종합 평가 보고서 생성", use_container_width=True)

def clean_markdown_text(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

# 3. 모던 게이지 바 도형 생성 함수 (일반 지표용)
def create_modern_gauge_drawing(title, definition, score, low_desc, high_desc):
    d = Drawing(535, 52)
    d.add(Rect(0, 0, 535, 52, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.8, rx=5, ry=5))
    
    d.add(String(12, 38, title, fontName='NanumGothicBold', fontSize=9.5, fillColor=colors.HexColor('#1E293B')))
    d.add(String(135, 39, f"[{definition}]", fontName='NanumGothic', fontSize=7.5, fillColor=colors.HexColor('#64748B')))
    
    normalized_score = int((score / 20.0) * 100)
    grade = "중간 (M)"
    badge_color = colors.HexColor('#3B82F6')
    if normalized_score <= 40:
        grade = "낮음 (L)"
        badge_color = colors.HexColor('#EF4444')
    elif normalized_score >= 76:
        grade = "높음 (H)"
        badge_color = colors.HexColor('#10B981')

    d.add(String(445, 38, f"환산점수: {normalized_score}점 [{grade}]", fontName='NanumGothicBold', fontSize=8.5, fillColor=badge_color))
    
    d.add(Rect(135, 18, 280, 7, fillColor=colors.HexColor('#E2E8F0'), strokeColor=None, rx=3.5, ry=3.5))
    bar_w = (normalized_score / 100.0) * 280
    d.add(Rect(135, 18, bar_w, 7, fillColor=badge_color, strokeColor=None, rx=3.5, ry=3.5))
    
    d.add(String(12, 6, f"• 낮음 특성: {low_desc}", fontName='NanumGothic', fontSize=7, fillColor=colors.HexColor('#64748B')))
    d.add(String(300, 6, f"• 높음 특성: {high_desc}", fontName='NanumGothic', fontSize=7, fillColor=colors.HexColor('#64748B')))
    
    return d

# 4. 에니어그램 핵심 성향 도표 생성 함수 (신규 추가)
def create_enneagram_gauge_drawing(enneagram_type, core_motivation, integration_stress):
    d = Drawing(535, 45)
    d.add(Rect(0, 0, 535, 45, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.8, rx=5, ry=5))
    
    d.add(String(12, 31, f"에니어그램 핵심 유형: Type {enneagram_type}", fontName='NanumGothicBold', fontSize=9.5, fillColor=colors.HexColor('#1E3A8A')))
    d.add(String(165, 32, f"[핵심 동기 및 집착: {core_motivation}]", fontName='NanumGothic', fontSize=7.5, fillColor=colors.HexColor('#64748B')))
    
    d.add(String(12, 12, f"• 통합(성장) 방향: {integration_stress.split('|')[0]}", fontName='NanumGothic', fontSize=7.5, fillColor=colors.HexColor('#10B981')))
    d.add(String(280, 12, f"• 분열(스트레스) 방향: {integration_stress.split('|')[1]}", fontName='NanumGothic', fontSize=7.5, fillColor=colors.HexColor('#EF4444')))
    
    return d

# 5. 2페이지 고정형 PDF 생성 함수
def create_pdf(text_page1, text_page2, user_name, motiv_scores, ennea_info):
    filename = f"{user_name}_Executive_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=22, bottomMargin=22)
    
    font_path = "NanumGothic.ttf"
    bold_path = "NanumGothicBold.ttf"
    if not os.path.exists(bold_path): bold_path = font_path
    
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
        pdfmetrics.registerFont(TTFont('NanumGothicBold', bold_path))
    except:
        pass
    
    title_style = ParagraphStyle('MainTitle', fontName='NanumGothicBold', fontSize=12, textColor=colors.white, alignment=TA_CENTER)
    header_style = ParagraphStyle('SectionHeader', fontName='NanumGothicBold', fontSize=9.5, textColor=colors.white, alignment=TA_CENTER)
    sub_style = ParagraphStyle('SubHeader', fontName='NanumGothicBold', fontSize=8, textColor=colors.HexColor('#1E3A8A'), spaceBefore=3, spaceAfter=1)
    body_style = ParagraphStyle('Body', fontName='NanumGothic', fontSize=7.2, leading=10, textColor=colors.HexColor('#334155'))
    comment_style = ParagraphStyle('Comment', fontName='NanumGothic', fontSize=7.2, leading=10, textColor=colors.HexColor('#1E3A8A'))
    th_style = ParagraphStyle('TableHeader', fontName='NanumGothicBold', fontSize=7.2, alignment=TA_CENTER, textColor=colors.HexColor('#1E293B'))
    td_style = ParagraphStyle('TableData', fontName='NanumGothic', fontSize=7, leading=9.5, alignment=TA_LEFT)

    story = []
    
    # -------------------------------------------------------------------------
    # [PAGE 1] 기질, 심리 동기 및 에니어그램 도표 진단 결과
    # -------------------------------------------------------------------------
    banner1 = Table([[Paragraph(f"<b>EXECUTIVE INTELLIGENCE REPORT (1/2) &nbsp;|&nbsp; {user_name}</b>", title_style)]], colWidths=[535], rowHeights=[22])
    banner1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(banner1)
    story.append(Spacer(1, 3))
    
    # 에니어그램 도표 추가 배치
    story.append(create_enneagram_gauge_drawing(ennea_info[0], ennea_info[1], ennea_info[2]))
    story.append(Spacer(1, 2))

    story.append(create_modern_gauge_drawing("1. 완벽성 및 원칙 지향", "규율 준수 및 세부 사항 통제", motiv_scores[0], "유연하나 실수가 잦음", "철저한 기준 준수, 정교함"))
    story.append(Spacer(1, 2))
    story.append(create_modern_gauge_drawing("2. 조력 및 공감 지향", "타인 감정 수용 및 협조 성향", motiv_scores[1], "독립적 선호, 타인 무관심", "뛰어난 공감, 화합 주도"))
    story.append(Spacer(1, 2))
    story.append(create_modern_gauge_drawing("3. 성취 및 목표 지향", "결과물 창출과 높은 성취 집념", motiv_scores[2], "안정 위주, 도전 의지 부족", "강한 목표 달성력, 추진력"))
    story.append(Spacer(1, 2))
    story.append(create_modern_gauge_drawing("4. 탐구 및 분석 지향", "원인 분석 및 지적 호기심의 깊이", motiv_scores[3], "표피적 이해에 머무름", "구조 분석 및 본질 통찰"))
    story.append(Spacer(1, 2))
    story.append(create_modern_gauge_drawing("5. 열정 및 비전 지향", "미래 가치 추구 및 변화 몰입도", motiv_scores[4], "현실 안주 성향", "혁신적 아이디어, 높은 몰입"))
    story.append(Spacer(1, 3))
    
    # 도표 하단 종합 분석 코멘트 박스
    comment_text = "<b>[전문가 진단 코멘트]:</b> 에니어그램 성향 및 5대 내면 동기 지표를 종합한 결과, 대상자는 높은 원칙 준수 성향과 치밀한 분석력을 겸비하고 있어 고난도 실무 환경에서 탁월한 안정성을 발휘합니다. 통합 방향의 성장을 위해 유연한 수용 태도를 병행하는 것이 효과적입니다."
    comment_table = Table([[Paragraph(comment_text, comment_style)]], colWidths=[535])
    comment_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#BFDBFE')),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(comment_table)
    story.append(Spacer(1, 3))
    
    for line in text_page1.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('## '):
            sec = Table([[Paragraph(line[3:], header_style)]], colWidths=[535], rowHeights=[15])
            sec.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E3A8A')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(sec)
            story.append(Spacer(1, 2))
        elif line.startswith('### '):
            story.append(Paragraph(clean_markdown_text(line[4:]), sub_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {clean_markdown_text(line[2:])}", body_style))
            story.append(Spacer(1, 1))
        else:
            story.append(Paragraph(clean_markdown_text(line), body_style))
            story.append(Spacer(1, 1))

    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # [PAGE 2] 마스터 액션 플랜 및 전략 과제표
    # -------------------------------------------------------------------------
    banner2 = Table([[Paragraph(f"<b>MASTER ACTION PLAN & STRATEGY (2/2) &nbsp;|&nbsp; {user_name}</b>", title_style)]], colWidths=[535], rowHeights=[22])
    banner2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(banner2)
    story.append(Spacer(1, 4))

    table_data = []
    for line in text_page2.split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('|'):
            if '---' in line: continue
            cols = [c.strip() for c in line.split('|')[1:-1]]
            row_cells = [Paragraph(clean_markdown_text(col), th_style) if len(table_data) == 0 else Paragraph(clean_markdown_text(col), td_style) for col in cols]
            table_data.append(row_cells)
            continue
        
        if table_data:
            t = Table(table_data, colWidths=[85, 175, 275])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F8FAFC')),
            ]))
            story.append(t)
            story.append(Spacer(1, 3))
            
            # 표 하단 전용 인사이트 코멘트 박스
            table_comment = "<b>[전략 실행 가이드 코멘트]:</b> 상단 마스터 플랜 과제표는 단기적 역량 보완과 장기적 리더십 확장을 동시에 달성할 수 있도록 설계되었습니다. 주간 단위 점검과 피드백 루프를 통해 실행력을 극대화하세요."
            t_comment_box = Table([[Paragraph(table_comment, comment_style)]], colWidths=[535])
            t_comment_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
                ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#BFDBFE')),
                ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t_comment_box)
            story.append(Spacer(1, 3))
            table_data = []

        if line.startswith('## '):
            sec2 = Table([[Paragraph(line[3:], header_style)]], colWidths=[535], rowHeights=[15])
            sec2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E3A8A')), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(sec2)
            story.append(Spacer(1, 2))
        elif line.startswith('### '):
            story.append(Paragraph(clean_markdown_text(line[4:]), sub_style))
        elif line.startswith('- '):
            story.append(Paragraph(f"• {clean_markdown_text(line[2:])}", body_style))
            story.append(Spacer(1, 1))
        else:
            story.append(Paragraph(clean_markdown_text(line), body_style))
            story.append(Spacer(1, 1))
            
    if table_data:
        t = Table(table_data, colWidths=[85, 175, 275])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#F8FAFC'))]))
        story.append(t)
        story.append(Spacer(1, 3))
        t_comment_box = Table([[Paragraph("<b>[전략 실행 가이드 코멘트]:</b> 상단 마스터 플랜 과제표는 단기적 역량 보완과 장기적 리더십 확장을 동시에 달성할 수 있도록 설계되었습니다.", comment_style)]], colWidths=[535])
        t_comment_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')), ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor('#BFDBFE')), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
        story.append(t_comment_box)

    doc.build(story)
    return filename

# 6. AI 실행 및 화면 출력
if submitted:
    if not name: 
        st.warning("성명을 입력해주세요.")
    else:
        with st.spinner("💎 에니어그램 도표 및 심층 분석 코멘트가 포함된 프리미엄 보고서를 생성 중입니다..."):
            client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))
            
            system_prompt = """
            # ROLE: 글로벌 최고 경영 컨설턴트 및 프리미엄 조직 심리 전략가
            # RULES & CONSTRAINTS:
            1. 절대 금지 사항: '사주', '명리', '별자리', 'MBTI' 등 진단 출처 명칭 직접 언급 금지. 전문 비즈니스/심리 용어 사용.
            2. 내용 풍성화 및 상세화: 빈칸과 여백이 남지 않도록 모든 항목별로 매우 상세하고 깊이 있는 문장으로 가득 채워 작성할 것.
            3. 마스터플랜 다양화: [인지/사유 고도화], [소통/관계 협업], [실무 실행력 강화], [자기관리/스트레스 루틴] 등 다채로운 영역으로 구체화할 것.
            4. 출력 형식: 반드시 아래의 구분자(`---PAGE_SPLIT---`)를 기준으로 페이지 1과 페이지 2 내용으로 나누어 출력할 것.
            
            # OUTPUT FORMAT:
            ## 심리 동기 및 행동 패턴 심층 분석
            - **고유 에너지 원천과 동기 구조**: (최소 4~5문장 이상으로 매우 상세하고 입체적으로 기술)
            - **성격적 강점과 현업 업무 스타일**: (최소 4~5문장 이상으로 구체적인 업무 상황과 연계하여 기술)
            - **무의식적 스트레스 요인 및 대응 메커니즘**: (구체적인 스트레스 유발 상황과 심리적 방어 기제 분석을 상세히 기술)
            
            ## 직무 적합도 및 핵심 역량 정밀 진단
            - **강점 극대화 영역 및 발휘 시나리오**: (실무 현장에서의 구체적 성과 창출 시나리오를 상세히 기술)
            - **잠재적 리스크 관리 및 보완 전략**: (발생 가능한 부작용과 이를 예방하기 위한 구체적 행동 지침 기술)
            ---PAGE_SPLIT---
            ## 역량 다각화 및 사유의 지평 확장
            - **인문교양 기반 통섭적 사고 배양**: (상세한 학습 방향 및 실천적 의의 기술)
            - **다원적 토론 세션을 통한 커뮤니케이션 유연성 확보**: (타인과의 상호작용 방식 개선 방안 기술)
            - **메타인지 기반 자기 객관화 및 루틴 체계화**: (자기 점검 및 성찰 시스템 구축 방안 기술)
            
            ## Master Action Plan & 다차원 전략 과제표
            | 영역 구분 | 역량 진단 요약 | 맞춤형 성장 액션 플랜 (단기~장기) |
            | :--- | :--- | :--- |
            | **인문 통섭 학습** | (진단 내용을 구체적으로 요약) | (고전 정독, 비판적 에세이 작성, 통섭적 주제 탐구 등 상세 실행 과제) |
            | **토론·소통 역량** | (진단 내용을 구체적으로 요약) | (소크라테스식 토론 세미나 참여, 그룹 피드백 세션 운영 등 상세 과제) |
            | **사유 체계 고도화** | (진단 내용을 구체적으로 요약) | (메타인지 일지 작성, 논리적 프레임워크 구축 및 정기 성찰) |
            | **실무 실행 및 루틴** | (진단 내용을 구체적으로 요약) | (업무 프로세스 최적화, 리스크 모니터링 체계 수립 및 주간 점검) |
            
            ## 종합 마스터플랜 실행 가이드
            - **단계별 실행 로드맵 및 주기적 성과 모니터링 수립**: (구체적 시나리오 및 실행 주기를 상세히 제시)
            - **현업 적용을 위한 피드백 루프 및 상시 점검 체계 구축**: (현업 연계 방안 및 성과 평가 지표 설정 방안 제시)
            """
            
            user_data = f"- 이름: {name}, 직무: {job}\n- 프로필코드: {mbti}, 생년월일: {birth}, 혈액형: {blood_type}\n- 내면동기척도: 완벽({e1}),조력({e2}),성취({e3}),독창({e4}),탐구({e5}),책임({e6}),열정({e7}),결단({e8}),조화({e9})"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                temperature=0.6, 
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_data}]
            )
            raw_content = response.choices[0].message.content.strip()
            
            if "---PAGE_SPLIT---" in raw_content:
                page1_text, page2_text = raw_content.split("---PAGE_SPLIT---")
            else:
                parts = raw_content.split("## 역량 다각화")
                page1_text = parts[0]
                page2_text = "## 역량 다각화" + parts[1] if len(parts) > 1 else raw_content
            
            st.success("💎 에니어그램 도표와 풍성한 분석 내용이 포함된 2페이지 통합 보고서가 완성되었습니다.")
            
            # 웹 화면 출력
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            st.markdown("### [PAGE 1] 기질, 에니어그램 및 심리 동기 진단 결과")
            st.markdown(page1_text)
            st.markdown("---")
            st.markdown("### [PAGE 2] 인문교양·토론 및 마스터 액션 플랜")
            st.markdown(page2_text)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 에니어그램 더미 데이터 (유형 1번 기준 예시: 통합 7번, 분열 4번)
            ennea_mock_info = ("Type 1 (개혁가형)", "완벽성, 올바름, 원칙 추구", "Type 7 (열정·낙천) | Type 4 (감정·개인주의)")
            
            # PDF 다운로드 버튼
            pdf_file = create_pdf(page1_text, page2_text, name, [e1, e2, e3, e4, e7], ennea_mock_info)
            with open(pdf_file, "rb") as f:
                st.download_button("📕 프리미엄 PDF 보고서 다운로드", data=f, file_name=pdf_file, mime="application/pdf", use_container_width=True)
