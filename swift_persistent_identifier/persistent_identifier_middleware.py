from .persistent_identifier_client import create_pid, delete_pid
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
        """
        If called with header X-Pid-Create and Method PUT become active and
        create a PID and store it with the object
        :param env: request environment
        :param start_response: function that we call when creating response
        :return:
        """
        self.start_response = start_response
        request = Request(env)
        if request.method == 'PUT':
            # try:
            #     (version, account, container, objname) = \
            #         split_path(request.path_info, 4, 4, True)
            # except ValueError:
            #     return self.app(env, start_response)
            # self.logger.debug('{},{},{},{}'.format(version,
            #                                        account,
            #                                        container,
            #                                        objname))
            if 'X-Pid-Create' in list(request.headers.keys()):
                url = '{}{}'.format(request.host_url, request.path_info)
                self.logger.info('Create a PID for {}'.format(url))
                success, pid = create_pid(object_url=url,
                                          api_url=self.conf.get('api_url'),
                                          username=self.conf.get('username'),
                                          password=self.conf.get('password'))
                if success:
                    request.headers['X-Object-Meta-PID'] = pid
                    response = PersistentIdentifierResponse(
                        pid=request.headers['X-Object-Meta-PID'],
                        username=self.conf.get('username'),
                        password=self.conf.get('password'),
                        start_response=start_response,
                        logger=self.logger)
                    return self.app(env, response.finish_response)
                else:
                    return Response(
                        status=502,
                        body='Could not contact PID API')(env, start_response)
        return self.app(env, start_response)


class PersistentIdentifierResponse(object):
    """
    Class that is created during request and that add X-Persistent-Identifier
    header to the response if a Persistent Identifier was requested
    """
    def __init__(self, pid, username, password, start_response, logger):
        """
        Hold pid url and credentials for response creation
        :param pid: persistent identifier url
        :param username: username for pid service
        :param password: password for pid service
        :param start_response: function that we call after we are finished
        :param logger: swift logger for logging
        :return: -
        """
        self.pid = pid
        self.username = username
        self.password = password
        self.start_response = start_response
        self.logger = logger

    def finish_response(self, status, headers):
        """
        Visited while creating the response
        :param status: status of the former middlewares and apps
        :param headers: headers of the former middlewares and apps
        :return: -
        """
        if int(status.split(' ')[0]) == 201:
            headers.append(('Persistent-Identifier', self.pid))
        else:
            delete_pid(pid_url=self.pid,
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
