from persistent_identifier_client import create_pid, delete_pid
from swift.common.utils import get_logger, split_path
from webob import Request, Response

class PersistentIdentifierMiddleware(object):
    """
    PID Middleware that creates PIDs for incoming objects if requested
    """
    def __init__(self, app, conf=None, logger=None):
        self.app = app
        if conf:
            self.conf = conf
        else:
            conf = {}
        if logger:
            self.logger = logger
        else:
            self.logger = get_logger(conf=conf,
                                     log_route='persistend-identifier',
                                     log_to_console=True)

    def __call__(self, env, start_response):
        self.start_response = start_response
        request = Request(env)
        if request.method == 'PUT':
            try:
                (version, account, container, objname) = \
                    split_path(request.path_info, 4, 4, True)
            except ValueError:
                return self.app(env, start_response)
            self.logger.info('{},{},{},{}'.format(version,
                                                  account,
                                                  container,
                                                  objname))
            if 'X-Pid-Create' in request.headers.keys():
                self.logger.info('Create a PID')
                success, pid = create_pid(object_url='tmp',
                                          api_url=self.conf.get('api_url'),
                                          username=self.conf.get('username'),
                                          password=self.conf.get('password'))
                if success:
                    request.headers['X-Object-Meta-PID'] = pid
                    response = PersistentIdentifierResponse(
                        headers=request.headers,
                        username=self.conf.get('username'),
                        password=self.conf.get('password'),
                        start_response=start_response,
                        logger=self.logger)
                    return self.app(env, response.finish_response)
                else:
                    return Response(status=502,
                                    body='Could not contact PID API')\
                        (env, start_response)
        return self.app(env, start_response)


class PersistentIdentifierResponse(object):

    def __init__(self, headers, username, password, start_response, logger):
        self.headers = headers
        self.username = username
        self.password = password
        self.start_response = start_response
        self.logger = logger

    def finish_response(self, status, headers):
        if int(status.split(' ')[0]) == 201:
            headers.append(('Persistent-Identifier',
                            self.headers['X-Object-Meta-PID']))
        else:
            delete_pid(pid_url=self.headers['X-Object-Meta-PID'],
                       username=self.username,
                       password=self.password)
        self.start_response(status, headers)

def filter_factory(global_config, **local_conf):
    """
    Returns a WSGI filter app for use with paste.deploy.
    """
    conf = global_config.copy()
    conf.update(local_conf)

    def persistent_identifier(app):
        return PersistentIdentifierMiddleware(app, conf)
    return persistent_identifier
