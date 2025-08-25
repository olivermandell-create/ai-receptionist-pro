import re

def parse_intent(text: str):
    t = (text or "").lower().strip()
    if any(k in t for k in ["hi","hello","hey"]):
        return {"type": "greeting", "response": "Hello! I can help you book, cancel, or reschedule."}
    if any(k in t for k in ["hours","address","location"]):
        return {"type": "faq", "response": "We're open most days from 9 AM to 6 PM. Would you like to book an appointment?"}
    if any(k in t for k in ["book","appointment","reserve","reservation","schedule"]):
        name = None
        m = re.search(r"my name is ([a-zA-Z ]+)", t)
        if m: name = m.group(1).title()
        when = None
        m = re.search(r"(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week|\d+ (am|pm))", t)
        if m: when = m.group(0)
        service = None
        m = re.search(r"for (a )?(consultation|cleaning|grooming|dinner|haircut|checkup|visit)", t)
        if m: service = m.group(2)
        return {"type":"book","name":name,"when":when,"service":service}
    if "cancel" in t:
        return {"type":"cancel","when":None}
    if any(k in t for k in ["reschedule","move","change time","change my appointment"]):
        return {"type":"reschedule","from_when":None,"to_when":None}
    return {"type":"unknown"}
