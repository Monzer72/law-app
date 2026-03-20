from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from PyPDF2 import PdfReader

app = FastAPI()

# السماح للواجهة بالاتصال بالمحرك
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/ask")
async def ask_lawyer(message: str = Form(...)):
    try:
        reader = PdfReader("sy-penal-code.pdf")
        text = ""
        # قراءة أول 30 صفحة فقط لضمان سرعة الرد وعدم حدوث ضغط
        for page in reader.pages[:30]:
            text += page.extract_text()
            
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"أنت مساعد قانوني سوري خبير. من خلال النص التالي: {text}\n\nأجب بدقة على: {message}"
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        return {"answer": "عذراً، حدث خطأ في معالجة النص. تأكد من أن ملف الـ PDF مرفوع بشكل صحيح."}
