#!/usr/bin/python3

# Bottle manuals:
# - https://bottlepy.org/docs/dev
# - https://bottlepy.org/docs/dev/stpl.html - template syntax description

from bottle import run, post, request
import datetime
import os

lastip: str = None
lastts: datetime = None
surveysfolder: str = "surveys"

def return_html_message(message: str):

    return f"""
    <html>
        <body style="background-color:black;color: white;display:flex; flex-direction:column; justify-content:center; min-height:100vh;text-align:center;">
            <h1>{message}</h1>
        </body>
    </html>
    """

@post('/submit')
def do_submit():

    global lastip, lastts, surveysfolder

    # basic protection against fuzzing and DDoS: no more than 4 submissions per minute is allowed from the same client
    ip: str = request.remote_addr # The client IP as a string. Note that this information can be forged by malicious clients.
    ts: datetime = datetime.datetime.now()
    if (lastip is not None):
        if (ip == lastip) and ((ts - lastts).total_seconds() < 15):
            return return_html_message("Submission is not accepted")
    lastip = ip
    lastts = ts

    # sanity check: candidate name must be present
    candidate_id: str = request.forms.get("candidate_id")
    if candidate_id is None:
        return return_html_message("Submission is not accepted:<br>specify your name at the 2nd page")
    if candidate_id.strip() == "":
        return return_html_message("Submission is not accepted:<br>specify your name at the 2nd page")
    # remove characters that are not letter or numbers
    candidate_id = ''.join(ch for ch in candidate_id if ch.isalnum())
    if candidate_id == "":
        return return_html_message("Submission is not accepted:<br>specify your name at the 2nd page")

    try:
        filename = os.path.join(os.getcwd(), surveysfolder, ts.strftime(f"%Y-%m-%d_%H-%M-%S_{candidate_id}.txt"))
        with open(filename, "w") as file:

            # extract all values from POST
            for key in request.forms:
                value = request.forms.get(key)
                file.write(f"{key}\t=\t{value}\n")
    except:
        return return_html_message("Submission is not accepted")

    return return_html_message("Submitted")
    
def main():
    print("Starting server...")
    run(host='localhost', port=8080, debug=True)

if __name__ == "__main__":
    main()