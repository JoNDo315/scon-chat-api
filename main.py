from fastapi import FastAPI, Response
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

app = FastAPI()

@app.get("/")
def generate_chat_image(users: str, msgs: str):
    user_list = users.split(",")
    msg_list = msgs.split(",")
    
    width, height = 600, 40 + (len(user_list) * 35)
    image = Image.new("RGBA", (width, height), (20, 20, 20, 230))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("malgun.ttf", 14)
    except:
        font = ImageFont.load_default()
        
    y_offset = 10
    for u, m in zip(user_list, msg_list):
        username = urllib.parse.unquote(u)
        message = urllib.parse.unquote(m)
        
        if username == "System":
            text = f"System: {message}"
            color = (200, 200, 200)
        else:
            text = f"{username}: {message}"
            color = (255, 255, 255)
            
        draw.text((15, y_offset), text, fill=color, font=font)
        y_offset += 30
        
    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
