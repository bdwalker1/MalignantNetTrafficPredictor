import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, StreamingResponse, RedirectResponse
import uvicorn
from uuid import UUID

import src.MNTP_Website as webSite
import src.appvars as appvars
from src.appvars import is_uuid
import requests

demo = FastAPI()
demo.mount("/static", StaticFiles(directory="./webpage"), name="webpage")

__api_url = os.environ.get("MNTP_API_URL")
if not __api_url:
    __api_url = "http://127.0.0.1:8000"

appvars.init()
appvars.api_url = __api_url

@demo.get("/", name="API Demo Page")
async def root(session_id: UUID = None):
    session_id, session_data, is_new_session = appvars.get_session_data(session_id)
    if is_new_session:
        return RedirectResponse(url=F"/?session_id={str(session_id)}")
    reply = await webSite.landing_page(session_id, session_data)
    reply.headers['session_id'] = session_data.session_id
    return reply

@demo.get("/blank", name="API Demo Page", response_class=HTMLResponse)
async def blank():
    reply = HTMLResponse(" ")
    return reply

@demo.get("/favicon.ico")
async def favicon():
    return FileResponse("./webpage/favicon.ico")

@demo.post("/apicall")
async def apicall(endpoint: str, qstring: str, session_id: UUID = None):
    session_id, session_data, is_new_session = appvars.get_session_data(session_id)
    if is_new_session:
        return RedirectResponse(url=F"/?session_id={str(session_id)}")
    qstring = qstring.replace("%26", "&")
    headers={"accept": "application/json"}
    if is_uuid(session_data.api_session_id):
        headers["session_id"] = F"{session_data.api_session_id}"
        qstring = F"session_id={session_data.api_session_id}&{qstring}"
    apiresponse = requests.post(appvars.api_url + "/" + endpoint + "/?" + qstring, headers=headers, data={})
    if apiresponse.headers.get('session_id') != session_data.api_session_id:
        session_data.api_session_id = apiresponse.headers.get('session_id')
        appvars.update_session_data(session_id, session_data)
    if endpoint == "predictfromfile":
        async def stream_results():
            result_list = str(apiresponse.text).split("\n")
            for line in result_list:
                yield line + "\n"
        mediatype = "text/plain"
        headers = {
            "Content-Type": mediatype,
            "Content-Disposition": "attachment; filename=predictions.csv"
        }
        reply = StreamingResponse(stream_results(), media_type=mediatype,headers=headers)
    else:
        reply = PlainTextResponse(str(apiresponse.json()), headers={"session_id": session_data.session_id})
    return reply

if __name__ == "__main__":

    uvicorn.run(demo, host="0.0.0.0", port=80)
