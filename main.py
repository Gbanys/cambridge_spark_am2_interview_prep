import base64
import json
import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, WebSocket, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import azure.cognitiveservices.speech as speechsdk

from llm import generate_response
from question_bank import am2_question_bank

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "cambridge_spark_am2_practice" / "app" / "static"),
    name="static",
)

BASE_DIR = Path(__file__).resolve().parent / "app"

templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))


@app.get("/")
async def return_home_page(request: Request):
    return templates.TemplateResponse(
        "home.html",
        context={
            "request": request,
        }
    )

@app.get("/llm_interview")
async def return_interview_page(request: Request):
    return templates.TemplateResponse(
            "interviewer.html",
            context={
                "request": request,
            }
        )


@app.post("/text-to-speech")
async def text_to_speech(request: Request):
    retrieved_json = await request.json()
    text = retrieved_json["text"]
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ["SPEECH_SUBSCRIPTION_KEY"],
        region=os.environ["SPEECH_REGION"]
    )
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    audio_data = synthesizer.speak_text_async(text).get().audio_data
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    return {"audio": audio_base64}


@app.get("/llm_interview/settings")
async def return_interviee_settings_page(request: Request):
    return templates.TemplateResponse(
        "interviewee_settings.html",
        context={
            "request": request,
        }
    )

@app.get("/start_interview")
async def start_interview(request: Request, question_order_value, question_duration_value):
    return templates.TemplateResponse(
        "interview_room.html",
        context={
            "request": request,
            "question_order_value": question_order_value,
            "question_duration_value": question_duration_value,
            "am2_question_bank" : json.dumps(am2_question_bank),
        }
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if data['status'] == 'get_all_questions':
            await websocket.send_json({"type": "get_all_questions", "questions" : am2_question_bank})
        elif data['status'] == 'get_llm_response':
            await get_llm_reponse(websocket, data['question'])


async def get_llm_reponse(websocket, question):
    llm_reponse = generate_response(question)
    await websocket.send_json({"type": "generate_response", "response" : llm_reponse})



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)