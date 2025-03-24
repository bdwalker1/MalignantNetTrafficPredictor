from fastapi.responses import HTMLResponse

def html_page( title: str, content: str ):
    html_output = F"""
    <html>
    <head>
    <title>{title}</title>
    </head>
    <body>
    <h1>{title}</h1>
    <p>{content}</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_output, status_code=200)

def landing_page():
    return html_page("Malignant Network Traffic Predictor",
                     "Welcome to the app<br><br>"
                     "<a href=\"/docs/\">Go to the /docs/ page</a>")