import os
from fastapi import FastAPI, Depends, Request, Response, HTTPException, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, StreamingResponse
import uvicorn
from uuid import UUID
import src.MNTP_Website as web
import src.appvars as appvars
import requests

demo = FastAPI()
demo.mount("/static", StaticFiles(directory="./webpage"), name="webpage")

__api_url = os.environ.get("MNTP_API_URL")
if not(__api_url):
    __api_url = "http://127.0.0.1:8000"

appvars.init()
appvars.api_url = __api_url

@demo.get("/", name="API Demo Page", response_class=HTMLResponse)
async def root(response: Response, session_id: UUID = Cookie(None)):
    session_id, session_data = await appvars.get_session_data(session_id)
    reply = await web.landing_page(session_id, session_data)
    reply.set_cookie("session_id", session_id, max_age=900, secure=False, samesite='None', httponly=True)
    return reply

@demo.get("/blank", name="API Demo Page", response_class=HTMLResponse)
async def root(response: Response, session_id: UUID = Cookie(None)):
    session_id, session_data = await appvars.get_session_data(session_id)
    reply = HTMLResponse(" ")
    reply.set_cookie("session_id", session_id, max_age=900, secure=False, samesite='None', httponly=True)
    return reply

@demo.get("/favicon.ico")
async def favicon(request: Request):
    return FileResponse("./webpage/favicon.ico")

@demo.post("/apicall")
async def apicall(endpoint: str, qstring: str, response: Response, session_id: UUID = Cookie(None)):
    session_id, session_data = await appvars.get_session_data(session_id)
    qstring = qstring.replace("%26", "&")
    cookies = {}
    if session_data.api_cookies is not None:
        cookies = session_data.api_cookies
    headers={"accept": "application/json"}
    if session_data.api_session_id is not None:
        headers["Cookie"] = F"session_id={session_data.api_session_id}"
    apiresponse = requests.post(appvars.api_url + "/" + endpoint + "/?" + qstring, headers=headers, cookies=cookies, data={})
    session_data.api_cookies = apiresponse.cookies
    session_data.api_session_id = apiresponse.cookies.get("session_id")
    _ = await appvars.backend.update(session_id, session_data)
    output = "???????"
    if endpoint == "predictfromfile":
        async def stream_results():
            result_list = str(apiresponse.text).split("\n")
            for line in result_list:
                yield (line + "\n")
        mediatype = "text/plain"
        headers = {
            "Content-Type": mediatype,
            "Content-Disposition": "attachment; filename=predictions.csv"
        }
        reply = StreamingResponse(stream_results(), media_type=mediatype,headers=headers)
    else:
        reply = PlainTextResponse(str(apiresponse.json()))
    reply.set_cookie("session_id", session_id, max_age=900, secure=False, samesite='None', httponly=True)
    return reply

if __name__ == "__main__":

    uvicorn.run(demo, host="0.0.0.0", port=80)
