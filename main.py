from typing import Union
import os
from fastapi import FastAPI
from datetime import datetime
import json
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import uvicorn
import analyze_channels
import yt

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/reports", StaticFiles(directory="reports"), name="static")


@app.get("/gen_reports")
def gen_reports(key: str):
    if key == "iamchicken":
        analyze_channels.main()
    return "DONE"


@app.get("/fetch_new_trends")
def fetch_new_trends(key: str):
    if key == "iamchicken":
        yt.start()
    return "DONE"


@app.get("/show_detail_report")
def show_detail_report(phrases: str):
    today = datetime.today().strftime('%Y-%m-%d')
    ranked_phrases = json.load(open(f"reports/{today}/ranked_phrase.json"))
    return ranked_phrases[phrases]


@app.get("/show_best_phrases")
def show_best_phrases():
    today = datetime.today().strftime('%Y-%m-%d')
    ranked_phrases = json.load(open(f"reports/{today}/ranked_phrase.json"))
    best_phrases = [i for i in ranked_phrases]
    return {"best_phrases": best_phrases}


@app.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    today = datetime.today().strftime('%Y-%m-%d')
    ranked_phrases = json.load(open(f"reports/{today}/ranked_phrase.json"))
    # best_phrases = [i for i in ranked_phrases]
    img_path = f"reports/{today}/wordcloud.png"
    return templates.TemplateResponse("home.html", {"request": request, "ranked_phrases": ranked_phrases,
                                                    "img_path": img_path})


uvicorn.run(app, host="0.0.0.0", port=8080)
