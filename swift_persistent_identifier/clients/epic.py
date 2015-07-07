from requests import delete, post


def create_pid(object_url, api_url, username, password, parent=None):
    """
    Create a EPIC PIC that is pointing to the digital object we have stored
    :param object_url: absolute object url that the pid points to
    :param api_url: EPIC endpoint
    :param username: EPIC username
    :param password: EPIC password
    :return: (boolean, str)
    """
    payload = [{'type': 'URL', 'parsed_data': object_url}]
    if parent:
        payload.append({'type': 'EUDAT/PPID', 'parsed_data': parent})
    try:
        response = post(url=api_url,
                        json=payload,
                        auth=(username, password))
    except Exception as err:
        return False, str(err)

    if response.status_code == 201 and response.headers['Location']:
        return True, response.headers['Location']
    else:
        return False, str(response.status_code)


def delete_pid(pid_url, username, password):
    """
    Delete a PID. Only use this if we were not able to store a object
    :param pid_url: absolute url for the PID
    :param username: EPIC username
    :param password: EPIC password
    :return: (boolean, str)
    """
    try:
        response = delete(pid_url, auth=(username, password))
    except Exception as err:
        return False, str(err)

    if response.status_code == 204:
        return True, str(response.status_code)
    else:
        return False, str(response.status_code)
