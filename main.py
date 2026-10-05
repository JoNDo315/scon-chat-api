from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def generate_live_chat(users: str = None, msgs: str = None):
    # 파라미터가 없을 때는 빈 리스트로 시작 (가짜 디폴트 유저 제거)
    if not users or not msgs:
        user_list = []
        msg_list = []
    else:
        user_list = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        msg_list = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]

    # 배경 이미지(bg.png) 처리
    bg_css = "background-color: #141414;"
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_css = f"background-image: url('data:image/png;base64,{encoded_string}'); background-size: cover; background-position: center;"
        except:
            pass

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Scon Live Chat</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            {bg_css}
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            overflow: hidden;
            display: flex;
            justify-content: flex-start;
            align-items: flex-start;
            height: 100vh;
        }}
        .overlay-container {{
            width: 600px;
            background: rgba(0, 0, 0, 0.6);
            box-sizing: border-box;
            padding: 15px;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        .live-badge {{
            display: inline-block;
            background-color: #CC0000;
            color: white;
            font-weight: bold;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 4px;
            margin-bottom: 12px;
            width: fit-content;
        }}
        .chat-scroll-box {{
            height: 196px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 8px;
        }}
        .chat-item {{
            font-size: 13px;
            line-height: 1.4;
            animation: fadeInSlide 0.3s ease-out forwards;
        }}
        @keyframes fadeInSlide {{
            0% {{ opacity: 0; transform: translateY(15px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        .system-msg {{
            color: #AAAAAA;
        }}
        .username {{
            font-weight: bold;
        }}
        .message-text {{
            color: #FFFFFF;
        }}
        .input-box {{
            margin-top: 15px;
            background: rgba(32, 32, 32, 0.85);
            border-radius: 18px;
            padding: 8px 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .input-placeholder {{
            color: #888888;
            font-size: 11px;
        }}
        .heart {{
            color: #FF5A78;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="overlay-container">
        <div class="live-badge">LIVE</div>
        <div class="chat-scroll-box" id="chatBox"></div>
        <div class="input-box">
            <span class="input-placeholder">채팅에 참여하세요...</span>
            <span class="heart">♥</span>
        </div>
    </div>

    <script>
        const inputUsers = {str(user_list).replace("'", '"')};
        const inputMsgs = {str(msg_list).replace("'", '"')};
        
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
                div.innerHTML = `<span class="system-msg">System: ${{m}}</span>`;
            }} else {{
                const color = getColor(u);
                div.innerHTML = `<span class="username" style="color: ${{color}};">${{u}}</span><span class="message-text">: ${{m}}</span>`;
            }}

            chatBox.appendChild(div);

            if (chatBox.children.length > 7) {{
                chatBox.removeChild(chatBox.children[0]);
            }}
        }}

        // 전달받은 데이터가 있다면 순차적으로 화면에 띄우기
        if (inputUsers.length > 0 && inputMsgs.length > 0) {{
            let i = 0;
            // 초기 데이터 밀어넣기
            for (let j = 0; j < Math.min(4, inputUsers.length); j++) {{
                appendChat(inputUsers[i], inputMsgs[i]);
                i = (i + 1) % inputUsers.length;
            }}
            
            // 이후 파라미터 데이터를 순환하며 실시간으로 밀어올리기
            setInterval(() => {{
                appendChat(inputUsers[i], inputMsgs[i]);
                i = (i + 1) % inputUsers.length;
            }, 2500);
        }}
    </script>
</body>
</html>
"""
    return Response(content=html_content, media_type="text/html")
