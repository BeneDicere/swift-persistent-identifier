from .persistent_identifier_client \
    import add_pid_checksum, create_pid, delete_pid
from swift.common.utils import config_true_value, get_logger, split_path
from swift.proxy.controllers.base import get_object_info
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
        self.add_checksum = config_true_value(self.conf.get('add_checksum',
                                                            'False'))

        if logger:
            self.logger = logger
        else:
            self.logger = get_logger(conf=conf,
                                     log_route='persistent-identifier',
                                     log_to_console=False)

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
            if 'X-Pid-Create' in list(request.headers.keys()):
                url = '{}{}'.format(request.host_url, request.path_info)
                if 'X-Pid-Parent' in list(request.headers.keys()):
                    parent = request.headers['X-Pid-Parent']
                else:
                    parent = None
                success, pid = create_pid(object_url=url,
                                          api_url=self.conf.get('api_url'),
                                          username=self.conf.get('username'),
                                          password=self.conf.get('password'),
                                          parent=parent)
                if success:
                    self.logger.info('Created a PID for {}'.format(url))
                    request.headers['X-Object-Meta-PID'] = pid
                    response = PersistentIdentifierResponse(
                        pid=pid,
                        add_checksum=self.add_checksum,
                        username=self.conf.get('username'),
                        password=self.conf.get('password'),
                        start_response=start_response,
                        logger=self.logger)
                    return self.app(env, response.finish_response)
                else:
                    self.logger.error('Unable to create  a PID for {},'
                                      'because of {}'.format(url, pid))
                    return Response(
                        status=502,
                        body='Could not contact PID API')(env, start_response)
        elif request.method in ['GET', 'HEAD']:
            # only modify response if we have a request for a object
            try:
                split_path(request.path_info, 4, 4, True)
            except ValueError:
                return self.app(env, start_response)

            object_metadata = get_object_info(
                env=request.environ,
                app=self.app,
                swift_source='PersistentIdentifierMiddleware')['meta']
            if 'pid' in object_metadata.keys():
                response = PersistentIdentifierResponse(
                    pid='',
                    add_checksum='',
                    username='',
                    password='',
                    start_response=start_response,
                    logger=self.logger)
                return self.app(env, response.finish_response_pidurl)
        return self.app(env, start_response)


class PersistentIdentifierResponse(object):
    """
    Class that is created during request and that add X-Persistent-Identifier
    header to the response if a Persistent Identifier was requested
    """
    def __init__(self, pid, add_checksum, username,
                 password, start_response, logger):
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
        self.add_checksum = add_checksum
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
            headers.append(('X-Pid-Url', self.pid))
            if self.add_checksum:
                add_pid_checksum(pid_url=self.pid,
                                 checksum=dict(headers)['Etag'],
                                 username=self.username,
                                 password=self.password
                                 )
        else:
            delete_pid(pid_url=self.pid,
                       username=self.username,
                       password=self.password)
        self.start_response(status, headers)

    def finish_response_pidurl(self, status, headers):
        """
        If X-Object-Meta-Pid is in the response, substitute it with
        X-Pid-Url header.

        One could think this is double checked because we use get_object_info
        in the PersistentIdentifierMiddleware, but because get_object_info does
        not do any authorization, we should use this double check.

        :param status: status of the former middlewares and apps
        :param headers: headers of the former middlewares and apps
        :return: -
        """

        if int(status.split(' ')[0]) == 200:
            try:
                tmp = dict(headers)['X-Object-Meta-Pid']
                headers.remove(('X-Object-Meta-Pid', tmp))
                headers.append(('X-Pid-Url', tmp))
            except KeyError:
                self.logger.debug('Request for object without'
                                  'X-Object-Meta-Pid header')
        self.start_response(status, headers)


def filter_factory(global_config, **local_conf):
    """
    Returns a WSGI filter app for use with paste.deploy.
    :param global_config: global config
    :param local_conf: local config
    :return: PersistentIdentifierMiddleware
    """
    conf = global_config.copy()
    conf.update(local_conf)

    def persistent_identifier(app):
        return PersistentIdentifierMiddleware(app, conf)
    return persistent_identifier
