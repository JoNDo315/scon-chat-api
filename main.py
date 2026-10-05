from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
    sample_pool = [
        ("System", "채팅에 참여해 린이를 응원하세요!"),
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
    # 끊김 없는 완벽한 3배수 순환 루프
    looped_chats = chat_list + chat_list + chat_list

    # 1. 배경 이미지 (원본 규격 400x250)
    bg_tag = '<rect width="400" height="250" fill="#141414"/>'
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_tag = f'<image x="0" y="0" width="400" height="250" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except Exception:
            pass

    # 2. 원본 실측 규격 적용 (높이 150px 영역 안에 정확히 6개 노출)
    LINE_HEIGHT = 25
    START_Y = 64  # 첫 줄 텍스트 베이스라인
    
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

    # 3. 흔들림 없는 원본 스텝 키프레임 생성 (2초 주기: 1.7초 정지 + 0.3초 이동)
    step_duration = 2.0
    total_duration = total_items * step_duration
    
    keyframes_list = []
    for step in range(total_items):
        start_pct = (step / total_items) * 100
        hold_pct = ((step + 0.85) / total_items) * 100
        move_pct = ((step + 1.0) / total_items) * 100

        cur_y = -(step * LINE_HEIGHT)
        next_y = -((step + 1) * LINE_HEIGHT)

        keyframes_list.append(f"{start_pct:.2f}% {{ transform: translateY({cur_y}px); }}")
        keyframes_list.append(f"{hold_pct:.2f}% {{ transform: translateY({cur_y}px); }}")
        keyframes_list.append(f"{move_pct:.2f}% {{ transform: translateY({next_y}px); }}")

    keyframes_css = "\n        ".join(keyframes_list)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">
  <defs>
    <!-- 원본 실측 마스크: x="15" y="45" width="370" height="150" -->
    <clipPath id="chat-view-area">
      <rect x="15" y="45" width="370" height="150" />
    </clipPath>
    <style>
      .chat-text {{
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', -apple-system, sans-serif;
        font-size: 12px;
      }}
      @keyframes liveStepScroll {{
        {keyframes_css}
      }}
      #chatScrollGroup {{
        animation: liveStepScroll {total_duration}s linear infinite;
      }}
    </style>
  </defs>

  <!-- 1. 배경 -->
  {bg_tag}
  <rect width="400" height="250" fill="#000000" opacity="0.45"/>

  <!-- 2. 스크롤 채팅 영역 (정확히 6줄 노출 및 스텝 롤링) -->
  <g clip-path="url(#chat-view-area)">
    <g id="chatScrollGroup" transform="translate(18, 0)">
    {items_svg}
    </g>
  </g>

  <!-- 3. 상단 LIVE 배지 (원본 좌표: 15, 14) -->
  <g transform="translate(15, 14)">
    <rect width="42" height="20" rx="3" fill="#FF2D55"/>
    <text x="8" y="14" fill="#FFFFFF" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="10px">LIVE</text>
  </g>

  <!-- 4. 하단 입력창 UI (원본 좌표: 15, 204) -->
  <g transform="translate(15, 204)">
    <rect width="370" height="34" rx="17" fill="#202020" opacity="0.85"/>
    <text x="16" y="21" fill="#888888" font-family="'Malgun Gothic', sans-serif" font-size="11.5px">채팅에 참여하세요...</text>
    <text x="345" y="22" fill="#FF5A78" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="14px">♥</text>
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
