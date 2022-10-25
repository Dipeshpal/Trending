from fastapi import FastAPI
import uvicorn
from datetime import datetime
import json
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import analyze_channels
import yt
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/reports", StaticFiles(directory="reports"), name="static")

origins = ["*"]

app.add_middleware(SessionMiddleware, secret_key="12345")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/2_gen_reports")
async def gen_reports(key: str):
    if key == "iamchicken":
        analyze_channels.main()
    return "Report Generated"


@app.get("/1_fetch_new_trends")
def fetch_new_trends(key: str):
    if key == "iamchicken":
        yt.start()
    return "DONE"


# @app.get("/show_detail_report")
# def show_detail_report(phrases: str):
#     today = datetime.today().strftime('%Y-%m-%d')
#     ranked_phrases = json.load(open(f"reports/{today}/ranked_phrase.json"))
#     return ranked_phrases[phrases]


# @app.get("/show_best_phrases")
# def show_best_phrases():
#     today = datetime.today().strftime('%Y-%m-%d')
#     ranked_phrases = json.load(open(f"reports/{today}/ranked_phrase.json"))
#     best_phrases = [i for i in ranked_phrases]
#     return {"best_phrases": best_phrases}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        ranked_phrases = json.load(open(f"reports/{today}/ranked_phrase.json"))
        # best_phrases = [i for i in ranked_phrases]
        img_path = f"reports/{today}/wordcloud.png"
        return templates.TemplateResponse("home.html", {"request": request, "ranked_phrases": ranked_phrases,
                                                        "img_path": img_path})
    except Exception as e:
        print(e)
        return "<a href='/docs'>Generate First</a>"


uvicorn.run(app, host="0.0.0.0", port=8080)
