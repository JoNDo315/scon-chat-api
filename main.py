from fastapi import FastAPI, Response
import urllib.parse
import os
import base64
import json

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
    if not users or not msgs:
        user_list = []
        msg_list = []
    else:
        user_list = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        msg_list = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]

    bg_style = "background-color: #141414;"
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_style = f"background-image: url('data:image/png;base64,{encoded_string}'); background-size: cover; background-position: center; background-repeat: no-repeat;"
        except:
            pass

    js_user_list = json.dumps(user_list)
    js_msg_list = json.dumps(msg_list)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="350" viewBox="0 0 800 350">
  <foreignObject width="100%" height="100%">
    <div xmlns="http://www.w3.org/1999/xhtml">
      <style>
        * {{
            box-sizing: border-box;
        }}
        body, html {{
            margin: 0;
            padding: 0;
            width: 800px;
            height: 350px;
            background-color: #0d0d0d;
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            overflow: hidden;
        }}
        .overlay-container {{
            width: 800px;
            height: 350px;
            {bg_style}
            box-sizing: border-box;
            padding: 20px;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .overlay-container::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.55);
            z-index: 1;
        }}
        .live-badge, .chat-scroll-box, .input-box {{
            position: relative;
            z-index: 2;
        }}
        .live-badge {{
            display: inline-block;
            background-color: #FF2D55;
            color: #FFFFFF !important;
            font-weight: bold;
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 4px;
            margin-bottom: 12px;
            width: fit-content;
        }}
        .chat-scroll-box {{
            height: 200px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 8px;
        }}
        .chat-item {{
            font-size: 14px;
            line-height: 1.4;
            animation: fadeInSlide 0.3s ease-out forwards;
            word-break: break-all;
        }}
        @keyframes fadeInSlide {{
            0% {{ opacity: 0; transform: translateY(10px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        .input-box {{
            margin-top: 14px;
            background: rgba(32, 32, 32, 0.85);
            border-radius: 20px;
            padding: 10px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .input-placeholder {{
            color: #888888 !important;
            font-size: 13px;
        }}
        .heart {{
            color: #FF5A78 !important;
            font-weight: bold;
            font-size: 16px;
        }}
      </style>

      <div class="overlay-container">
          <div class="live-badge">LIVE</div>
          <div class="chat-scroll-box" id="chatBox"></div>
          <div class="input-box">
              <span class="input-placeholder">채팅에 참여하세요...</span>
              <span class="heart">♥</span>
          </div>
      </div>

      <script>
      //<![CDATA[
          const inputUsers = {js_user_list};
          const inputMsgs = {js_msg_list};
          
          const chatBox = document.getElementById('chatBox');
          
          const palette = ["#FF6E6E", "#6EE273", "#73BEFF", "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"];
          function getColor(name) {{
              let hash = 0;
              for (let i = 0; i < name.length; i++) {{
                  hash = name.charCodeAt(i) + ((hash << 5) - hash);
              }}
              return palette[Math.abs(hash) % palette.length];
          }}

          function appendChat(u, m) {{
              const div = document.createElement('div');
              div.className = 'chat-item';

              if (u === "System") {{
                  div.innerHTML = '<span style="color: #AAAAAA !important;">System: ' + m + '</span>';
              }} else {{
                  const color = getColor(u);
                  div.innerHTML = '<span style="color: ' + color + ' !important; font-weight: bold;">' + u + '</span><span style="color: #FFFFFF !important;">: ' + m + '</span>';
              }}

              chatBox.appendChild(div);

              if (chatBox.children.length > 7) {{
                  chatBox.removeChild(chatBox.children[0]);
              }}
          }}

          const samplePool = [
              ["System", "채팅에 참여해 스콘즈를 응원하세요!"],
              ["스콘팬1", "오늘 의상 진짜 미쳤다ㅠㅠㅠ"],
              ["김스콘", "실시간으로 보고 있는데 너무 떨려"],
              ["토끼단", "스콘즈 화이팅!! 언제나 응원해"],
              ["모찌", "노래 선곡 미쳤다 진짜"],
              ["별빛스콘", "댓글 읽어주세요 제발요ㅠㅠ"],
              ["체리", "오늘 라이브 레전드 찍네ㅋㅋㅋ"]
          ];

          const activeUsers = inputUsers.length > 0 ? inputUsers : samplePool.map(item => item[0]);
          const activeMsgs = inputMsgs.length > 0 ? inputMsgs : samplePool.map(item => item[1]);

          let index = 0;
          for (let j = 0; j < Math.min(4, activeUsers.length); j++) {{
              appendChat(activeUsers[index], activeMsgs[index]);
              index = (index + 1) % activeUsers.length;
          }}

          setInterval(() => {{
              appendChat(activeUsers[index], activeMsgs[index]);
              index = (index + 1) % activeUsers.length;
          }}, 2500);
      //]]>
      </script>
    </div>
  </foreignObject>
</svg>'''

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )
