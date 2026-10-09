from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
    # 모범 사례처럼 기본 안내 및 빈자리 보충용 시스템 풀
    system_fillers = [
        ("System", "채팅에 참여해 아이돌을 응원하세요!"),
        ("System", "깨끗한 채팅 문화를 만들어주세요."),
        ("System", "채팅에 참여해 아이돌을 응원하세요!"),
        ("System", "라이브 방송 시청 중입니다."),
        ("System", "채팅에 참여해 오시를 응원하세요!"),
        ("System", "응원 메시지를 남겨보세요!"),
        ("System", "채팅에 참여해 오시를 응원하세요!")
    ]

    palette = ["#FF6E6E", "#6EE273", "#73BEFF", "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"]
    def get_color(name):
        h = 0
        for ch in name:
            h = ord(ch) + ((h << 5) - h)
        return palette[abs(h) % len(palette)]

    # 1. 파라미터 파싱
    user_inputs = []
    if users and msgs:
        u_arr = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        m_arr = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]
        for u, m in zip(u_arr, m_arr):
            user_inputs.append((u, m))

    # 2. AI가 1~3개만 보내도 서버가 알아서 시스템 멘트로 7개까지 보충
    chat_list = []
    if user_inputs:
        chat_list = list(user_inputs)
        fill_idx = 0
        while len(chat_list) < 7:
            chat_list.append(system_fillers[fill_idx % len(system_fillers)])
            fill_idx += 1
    else:
        chat_list = system_fillers

    total_items = len(chat_list)
    looped_chats = chat_list + chat_list + chat_list

    # 3. 배경 이미지 (400x250)
    bg_tag = '<rect width="400" height="250" fill="#141414"/>'
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_tag = f'<image x="0" y="0" width="400" height="250" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except Exception:
            pass

    # 4. 규격 및 텍스트 렌더링
    LINE_HEIGHT = 25
    START_Y = 66
    
    text_elements = []
    for i, (u, m) in enumerate(looped_chats):
        y_pos = START_Y + (i * LINE_HEIGHT)
        if u == "System":
            text_elements.append(
                f'<text x="0" y="{y_pos}" class="chat-text" fill="#8E8E93">System: {m}</text>'
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

    # 5. 흔들림 없는 단방향 스텝 키프레임 (2초 주기)
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
    <clipPath id="chat-view-area">
      <rect x="0" y="42" width="400" height="158" />
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

  <!-- 배경 -->
  {bg_tag}
  <rect width="400" height="250" fill="#000000" opacity="0.45"/>

  <!-- 스크롤 채팅 그룹 -->
  <g clip-path="url(#chat-view-area)">
    <g id="chatScrollGroup" transform="translate(22, 0)">
    {items_svg}
    </g>
  </g>

  <!-- LIVE 배지 -->
  <g transform="translate(15, 14)">
    <rect width="42" height="20" rx="3" fill="#FF2D55"/>
    <text x="8" y="14" fill="#FFFFFF" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="10px">LIVE</text>
  </g>

  <!-- 하단 입력창 UI -->
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
