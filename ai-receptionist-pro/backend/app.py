import os, json
from fastapi import FastAPI, Request, Body
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse, Gather
from typing import Dict, Any

from models import init_db, SessionLocal, Tenant, Appointment, Customer
from scheduler import find_available_slot, create_appointment, cancel_appointment, reschedule_appointment
from nlu import parse_intent

load_dotenv()

app = FastAPI(title="AI Receptionist — Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h3>AI Receptionist — Pro backend running</h3>"

def tenant_for_call(to_number: str) -> int:
    raw = os.getenv("NUMBER_TENANT_MAP", "{}")
    try:
        mp = json.loads(raw)
    except Exception:
        mp = {}
    return mp.get(to_number, 1)

@app.post("/twilio/voice", response_class=PlainTextResponse)
async def twilio_voice(request: Request):
    form = await request.form()
    to_number = form.get("To", "")
    _tenant_id = tenant_for_call(to_number)

    vr = VoiceResponse()
    gather = Gather(input="speech", action="/twilio/voice/handle", method="POST", speechTimeout="auto")
    gather.say("Hi! You're speaking with the AI receptionist. How can I help you today? You can say book an appointment, cancel, or reschedule.")
    vr.append(gather)
    vr.say("Sorry, I didn't catch that.")
    vr.redirect("/twilio/voice")
    return PlainTextResponse(str(vr), media_type="application/xml")

@app.post("/twilio/voice/handle", response_class=PlainTextResponse)
async def twilio_voice_handle(request: Request):
    form = await request.form()
    speech = form.get("SpeechResult", "") or ""
    from_number = form.get("From", "") or ""
    to_number = form.get("To", "") or ""
    tenant_id = tenant_for_call(to_number)

    vr = VoiceResponse()
    intent = parse_intent(speech)

    if intent["type"] in ("greeting","faq"):
        vr.say(intent.get("response","Hello!"))
        vr.hangup()
        return PlainTextResponse(str(vr), media_type="application/xml")

    if intent["type"] == "book":
        when_text = intent.get("when")
        service = intent.get("service") or "appointment"
        name = intent.get("name") or "Caller"
        dt = find_available_slot(tenant_id=tenant_id, when_text=when_text)
        if not dt:
            vr.say("Sorry, no availability matched. Please try another time.")
            vr.hangup()
            return PlainTextResponse(str(vr), media_type="application/xml")
        _appt = create_appointment(tenant_id, from_number, name, dt, service)
        vr.say("You're booked. A confirmation will be sent.")
        vr.hangup()
        return PlainTextResponse(str(vr), media_type="application/xml")

    if intent["type"] == "cancel":
        ok = cancel_appointment(tenant_id, from_number, intent.get("when"))
        vr.say("Your appointment has been canceled." if ok else "I couldn't find that appointment to cancel.")
        vr.hangup()
        return PlainTextResponse(str(vr), media_type="application/xml")

    if intent["type"] == "reschedule":
        ok = reschedule_appointment(tenant_id, from_number, intent.get("from_when"), intent.get("to_when"))
        vr.say("You're rescheduled." if ok else "I couldn't reschedule that appointment.")
        vr.hangup()
        return PlainTextResponse(str(vr), media_type="application/xml")

    vr.say("Sorry, let's try again.")
    vr.redirect("/twilio/voice")
    return PlainTextResponse(str(vr), media_type="application/xml")
