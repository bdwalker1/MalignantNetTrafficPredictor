import json
from fastapi import FastAPI, Request
import uvicorn
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import src.MNTP_Website as web

demo = FastAPI()
demo.mount("/static", StaticFiles(directory="./webpage"), name="webpage")

@demo.get("/", name="API Demo Page", response_class=HTMLResponse)
async def root(request: Request):
    return web.landing_page(request.base_url)

@demo.get("/favicon.ico")
async def favicon(request: Request):
    return FileResponse("./webpage/favicon.ico")

if __name__ == "__main__":
    uvicorn.run(demo, host="0.0.0.0", port=80)
