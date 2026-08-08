from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import shutil
import os

app = FastAPI()

UPLOAD_DIR = "static_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

initial_writers = {}
for i in range(1, 11):
    initial_writers[f"writer{i}"] = {
        "name": f"작가 {i}",
        "chars": 0,
        "hours": "0시간 0분",
        "memo": "마감 파이팅!",
        "checked": False,
        "image": ""
    }

db: Dict[str, Any] = {
    "writers": initial_writers
}

@app.get("/", response_class=HTMLResponse)
def read_root():
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>작가 대통합⭐</title>
        <style>
            :root {{
                --bg-color: #f7f9f6;
                --text-color: #2f3e46;
            }}
            body {{
                font-family: 'Malgun Gothic', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 15px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 15px;
            }}
            .header h1 {{
                font-size: 24px;
                margin: 0 0 5px 0;
                color: #354f52;
            }}
            .header p {{
                font-size: 13px;
                margin: 0;
                color: #666;
            }}
            /* 한 화면에 아기자기하게 모여드는 그리드 레이아웃 */
            .container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 12px;
                max-width: 1300px;
                margin: 0 auto;
            }}
            /* 컴팩트하고 귀여운 카드 박스 */
            .card {{
                border-radius: 12px;
                padding: 12px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                display: flex;
                flex-direction: column;
                gap: 5px;
                font-size: 12px;
                transition: background 0.3s;
            }}
            .card select, .card input[type="text"], .card input[type="number"], .card textarea {{
                width: 100%;
                padding: 4px 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
                font-size: 11px;
            }}
            .card label {{
                font-weight: bold;
                font-size: 11px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            .preview-img {{
                width: 100%;
                height: 70px;
                object-fit: cover;
                border-radius: 6px;
                background: #fff;
                border: 1px dashed #ccc;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                color: #888;
            }}
            button.save-btn {{
                background-color: #52796f;
                color: white;
                border: none;
                padding: 6px;
                width: 100%;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                font-size: 11px;
                margin-top: 2px;
            }}
            button.save-btn:hover {{
                background-color: #354f52;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>작가 대통합⭐</h1>
            <p>우리들의 편안한 실시간 마감 공간</p>
        </div>

        <div class="container" id="card-container"></div>

        <script>
            async function loadData() {{
                const res = await fetch('/data');
                const data = await res.json();
                
                const container = document.getElementById('card-container');
                container.innerHTML = '';
                
                for (const [id, info] of Object.entries(data.writers)) {{
                    let imgTag = info.image ? `<img src="${{info.image}}" class="preview-img">` : `<div class="preview-img">사진/움짤 없음</div>`;
                    let selectedTheme = localStorage.getItem(`theme_${{id}}`) || 'naver';
                    
                    container.innerHTML += `
                        <div class="card" id="card_box_${{id}}" style="background-color: ${{getThemeColor(selectedTheme)}};">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <label style="font-size:10px;">테마</label>
                                <select onchange="changeCardTheme('${{id}}', this.value)" style="width:75px; font-size:10px;">
                                    <option value="naver" ${{selectedTheme === 'naver' ? 'selected' : ''}}>초록</option>
                                    <option value="ridi" ${{selectedTheme === 'ridi' ? 'selected' : ''}}>파랑</option>
                                    <option value="kakao" ${{selectedTheme === 'kakao' ? 'selected' : ''}}>노랑</option>
                                </select>
                            </div>

                            <label>작가 이름 <input type="text" value="${{info.name}}" id="name_${{id}}" style="width:110px;"></label>
                            
                            <label>출석 체크 <input type="checkbox" ${{info.checked ? 'checked' : ''}} id="check_${{id}}"></label>
                            
                            <label>글자수 <input type="number" value="${{info.chars}}" id="chars_${{id}}" style="width:110px;"></label>

                            <label>작업시간 <input type="text" value="${{info.hours}}" id="hours_${{id}}" style="width:105px;"></label>
                            
                            <div>
                                <label style="margin-bottom:2px;">사진/움짤</label>
                                <input type="file" id="file_${{id}}" accept="image/*" style="font-size:10px; width:100%;">
                            </div>
                            ${{imgTag}}
                            
                            <div>
                                <label style="margin-bottom:2px;">메모</label>
                                <textarea id="memo_${{id}}" rows="1" style="font-size:11px;">${{info.memo}}</textarea>
                            </div>
                            
                            <button class="save-btn" onclick="saveData('${{id}}')">저장</button>
                        </div>
                    `;
                }}
            }}

            function getThemeColor(theme) {{
                if (theme === 'naver') return '#e8f5e9';
                if (theme === 'ridi') return '#e2eafc';
                if (theme === 'kakao') return '#fff3b0';
                return '#e8f5e9';
            }}

            function changeCardTheme(writerId, theme) {{
                localStorage.setItem(`theme_${{writerId}}`, theme);
                document.getElementById(`card_box_${{writerId}}`).style.backgroundColor = getThemeColor(theme);
            }}

            async function saveData(writerId) {{
                const name = document.getElementById(`name_${{writerId}}`).value;
                const checked = document.getElementById(`check_${{writerId}}`).checked;
                const chars = parseInt(document.getElementById(`chars_${{writerId}}`).value) || 0;
                const hours = document.getElementById(`hours_${{writerId}}`).value;
                const memo = document.getElementById(`memo_${{writerId}}`).value;
                const fileInput = document.getElementById(`file_${{writerId}}`);

                const formData = new FormData();
                formData.append("writer_id", writerId);
                formData.append("name", name);
                formData.append("chars", chars);
                formData.append("hours", hours);
                formData.append("memo", memo);
                formData.append("checked", checked);
                
                if (fileInput.files.length > 0) {{
                    formData.append("file", fileInput.files[0]);
                }}

                const res = await fetch('/update', {{
                    method: 'POST',
                    body: formData
                }});
                
                if (res.ok) {{
                    alert('저장되었습니다!');
                    loadData();
                }} else {{
                    alert('저장 실패 ㅠㅠ 다시 시도해줘!');
                }}
            }}

            loadData();
            setInterval(loadData, 5000);
        </script>
    </body>
    </html>
    """

@app.get("/data")
def get_data():
    return db

@app.post("/update")
async def update_writer(
    writer_id: str = Form(...),
    name: str = Form(...),
    chars: int = Form(...),
    hours: str = Form(...),
    memo: str = Form(...),
    checked: bool = Form(...),
    file: UploadFile = File(None)
):
    if writer_id in db["writers"]:
        image_path = db["writers"][writer_id]["image"]
        
        if file and file.filename:
            file_location = f"{UPLOAD_DIR}/{file.filename}"
            with open(file_location, "wb+") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_path = f"/{file_location}"

        db["writers"][writer_id].update({
            "name": name,
            "chars": chars,
            "hours": hours,
            "memo": memo,
            "checked": checked,
            "image": image_path
        })
    return {"status": "success"}
