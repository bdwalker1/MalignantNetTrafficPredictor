import json
from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import src.MNTP_Website as web
import requests

demo = FastAPI()
demo.mount("/static", StaticFiles(directory="./webpage"), name="webpage")

__api_url = "http://mntp-api.hopto.me"
# __api_url = "http://127.0.0.1:8000"

@demo.get("/", name="API Demo Page", response_class=HTMLResponse)
async def root(request: Request):
    return web.landing_page(__api_url)

@demo.get("/blank", name="API Demo Page", response_class=HTMLResponse)
async def root():
    return HTMLResponse(" ")

@demo.get("/favicon.ico")
async def favicon(request: Request):
    return FileResponse("./webpage/favicon.ico")

@demo.post("/apicall")
async def apicall(endpoint: str, qstring: str):
    qstring = qstring.replace("%26", "&")
    apiresponse = requests.post(__api_url + "/" + endpoint + "/?" + qstring, headers={"accept": "application/json"}, data={})
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
        return StreamingResponse(stream_results(), media_type=mediatype,headers=headers)
    else:
        output = str(apiresponse.json())
    # if endpoint == "predictfromjson":
    #     output = str(apiresponse.json())
    # if endpoint == "predictfile2file":
    #     output = apiresponse.text
    return PlainTextResponse(output)

if __name__ == "__main__":
    uvicorn.run(demo, host="0.0.0.0", port=80)
