from bottle import route, run, request, abort, static_file
from ordering_machine import OrderingMachine
import os

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
machine = {}

@route("/webhook", method = "GET")
def setup_webhook():
    """
        Setting up webhook.
    """
    mode = request.GET.get("hub.mode")
    token = request.GET.get("hub.verify_token")
    challenge = request.GET.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return challenge
    else:
        abort(403)

@route("/webhook", method = "POST")
def webhook_handler():
    """
        Handling message from user.
        Use event['sender']['id'] to identify session
    """
    body = request.json
    print(body)

    if body['object'] == "page":
        event = body['entry'][0]['messaging'][0]
        session_id = event['sender']['id']
        if not session_id in machine:
            machine[session_id] = OrderingMachine(session_id)
        else:
            machine[session_id].transit(event)
        return 'OK'

@route('/show-fsm', methods = ['GET'])
def show_fsm():
    #machine['<PSID>'].get_graph().draw('fsm.png', prog='dot', format='png')
    return static_file('fsm.png', root='./', mimetype='image/png')

if __name__ == "__main__":
    run(host="localhost", port=5000, debug=True, reloader=True)
