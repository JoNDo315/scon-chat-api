from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
    sample_pool = [
        ("System", "채팅에 참여해 스콘즈를 응원하세요!"),
        ("스콘팬1", "오늘 의상 진짜 미쳤다ㅠㅠㅠ"),
        ("김스콘", "실시간으로 보고 있는데 너무 떨려"),
        ("토끼단", "스콘즈 화이팅!! 언제나 응원해"),
        ("모찌", "노래 선곡 미쳤다 진짜"),
        ("별빛스콘", "댓글 읽어주세요 제발요ㅠㅠ"),
        ("체리", "오늘 라이브 레전드 찍네ㅋㅋㅋ")
    ]

    palette = ["#FF6E6E", "#6EE273", "#73BEFF", "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"]
    def get_color(name):
        h = 0
        for ch in name:
            h = ord(ch) + ((h << 5) - h)
        return palette[abs(h) % len(palette)]

    chat_list = []
    if users and msgs:
        u_arr = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        m_arr = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]
        for u, m in zip(u_arr, m_arr):
            chat_list.append((u, m))

    if not chat_list:
        chat_list = sample_pool

    total_items = len(chat_list)
    # 끊김 없는 완전 무한 루프를 위해 3세트 연속 배치
    looped_chats = chat_list + chat_list + chat_list

    # 1. 배경 이미지
    bg_tag = '<rect width="800" height="350" fill="#141414"/>'
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_tag = f'<image x="0" y="0" width="800" height="350" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except Exception:
            pass

    # 2. 모범 사례 규격 (화면 안에 딱 6~7개가 촘촘히 꽉 차도록 세팅)
    LINE_HEIGHT = 24  # 줄 간격 축소로 밀도감 형성
    START_Y = 120     # 첫 로딩부터 화면 가득 6~7줄이 균형 있게 보이도록 배치
    
    text_elements = []
    for i, (u, m) in enumerate(looped_chats):
        y_pos = START_Y + (i * LINE_HEIGHT)
        if u == "System":
            text_elements.append(
                f'<text x="0" y="{y_pos}" class="chat-text" fill="#AAAAAA">System: {m}</text>'
            )
        else:
            col = get_color(u)
            text_elements.append(
                f'<text x="0" y="{y_pos}" class="chat-text">'
                f'<tspan fill="{col}" font-weight="bold">{u}</tspan>'
                f'<tspan fill="#FFFFFF">: {m}</tspan>'
                f'</text>'
            )

    items_svg = "\n    ".join(text_elements)

    # 3. 멈춤(Hold)과 순간 도약(Snap)이 조화된 무한 계단 키프레임 생성
    step_duration = 2.0  # 한 메시지당 주기 (약 1.75초 정지 + 0.25초 찰나의 이동)
    total_duration = total_items * step_duration
    
    keyframes_list = []
    for step in range(total_items + 1):
        current_y = -(step * LINE_HEIGHT)
        
        # 이전 줄에서 방금 올라온 시점 (0.25초 동안 탄력 있게 올라옴)
        if step > 0:
            jump_end = ((step - 1 + 0.12) / total_items) * 100
            keyframes_list.append(f"{jump_end:.2f}% {{ transform: translateY({current_y}px); }}")
            
        # 다음 줄로 올라가기 전까지 가만히 머물며 읽히는 시점
        if step < total_items:
            hold_end = ((step + 0.88) / total_items) * 100
            keyframes_list.append(f"{hold_end:.2f}% {{ transform: translateY({current_y}px); }}")
            
    keyframes_css = "\n        ".join(keyframes_list)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="350" viewBox="0 0 800 350">
  <defs>
    <!-- 상하단 클리핑 마스크 -->
    <clipPath id="chat-view-area">
      <rect x="0" y="52" width="800" height="230" />
    </clipPath>
    <style>
      .chat-text {{
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', -apple-system, sans-serif;
        font-size: 13.5px;
      }}
      @keyframes liveStepScroll {{
        0% {{ transform: translateY(0px); }}
        {keyframes_css}
        100% {{ transform: translateY(-{total_items * LINE_HEIGHT}px); }}
      }}
      #chatScrollGroup {{
        animation: liveStepScroll {total_duration}s cubic-bezier(0.2, 0.9, 0.3, 1) infinite;
      }}
    </style>
  </defs>

  <!-- 1. 배경 -->
  {bg_tag}
  <rect width="800" height="350" fill="#000000" opacity="0.45"/>

  <!-- 2. 스크롤 채팅 영역 (화면에 6~7개가 차 있으며 위로 툭툭 올라감) -->
  <g clip-path="url(#chat-view-area)">
    <g id="chatScrollGroup" transform="translate(38, 0)">
    {items_svg}
    </g>
  </g>

  <!-- 3. 상단 LIVE 배지 -->
  <g transform="translate(20, 18)">
    <rect width="46" height="22" rx="4" fill="#FF2D55"/>
    <text x="10" y="15" fill="#FFFFFF" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="11px">LIVE</text>
  </g>

  <!-- 4. 하단 입력창 UI -->
  <g transform="translate(20, 290)">
    <rect width="760" height="42" rx="21" fill="#202020" opacity="0.85"/>
    <text x="22" y="26" fill="#888888" font-family="'Malgun Gothic', sans-serif" font-size="13px">채팅에 참여하세요...</text>
    <text x="725" y="27" fill="#FF5A78" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="16px">♥</text>
  </g>
</svg>'''

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )
