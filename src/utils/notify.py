import requests


def send_line_notify(exec_mode, line_notify_token, message):
    if exec_mode == "dev":
        return
    line_notify_api = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {line_notify_token}"}
    data = {"message": f"message: {message}"}
    rtn = requests.post(line_notify_api, headers=headers, data=data)
    return rtn.status_code
