from requests import delete, post

def create_pid(object_url, api_url, username, password):
    payload = [{'type': 'URL', 'parsed_data': object_url}]
    try:
        response = post(url=api_url,
                        json=payload,
                        auth=(username, password))
    except Exception as err:
        return False, str(err.message)

    if response.status_code == 201 and response.headers['Location']:
        return True, response.headers['Location']
    else:
        return False, str(response.status_code)


def delete_pid(pid_url, username, password):
    try:
        response = delete(pid_url, auth=(username, password))
    except Exception as err:
        return False, str(err.message)

    if response.status_code == 204:
        return True, str(response.status_code)
    else:
        return False, str(response.status_code)
