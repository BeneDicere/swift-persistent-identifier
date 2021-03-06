from unittest import TestCase
from swift_persistent_identifier.clients.epic \
    import create_pid, delete_pid, add_pid_checksum


class TestClientsEpic(TestCase):
    def setUp(self):
        self.username = '1234'
        self.password = '5678'
        self.api_url = 'http://localhost:5000/8441/'

    def test_create_pid(self):
        success, pid_url = create_pid(object_url='http://swift:88/v1/acc/d/f',
                                      api_url=self.api_url,
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, True)
        self.assertEqual(type(pid_url), str)

    def test_create_pid_with_parent(self):
        success, pid_url = create_pid(object_url='http://swift:88/v1/acc/d/f',
                                      api_url=self.api_url,
                                      username=self.username,
                                      password=self.password,
                                      parent='http://localhost/parent-pid')
        self.assertEqual(success, True)
        self.assertEqual(type(pid_url), str)

    def test_create_pid_fail(self):
        success, pid_url = create_pid(object_url='http://swift:88/v1/acc/d/f',
                                      api_url='http://localhost',
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, False)
        self.assertEqual(type(pid_url), str)

    def test_delete_pid(self):
        success, pid_url = create_pid(object_url='http://swift:88/v1/acc/d/f',
                                      api_url=self.api_url,
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, True)
        self.assertEqual(type(pid_url), str)

        success, message = delete_pid(pid_url=pid_url,
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, True)
        self.assertEqual(type(message), str)

    def test_delete_pid_twotimes(self):
        success, pid_url = create_pid(object_url='http://swift:88/v1/acc/d/f',
                                      api_url=self.api_url,
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, True)
        self.assertEqual(type(pid_url), str)

        success, message = delete_pid(pid_url=pid_url,
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, True)
        self.assertEqual(type(message), str)
        success, message = delete_pid(pid_url=pid_url,
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, False)
        self.assertEqual(type(message), str)

    def test_delete_pid_nonexisting(self):
        success, message = delete_pid(pid_url='http://localhost',
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, False)

    def test_update_pid(self):
        success, pid_url = create_pid(object_url='http://swift:88/v1/acc/d/f',
                                      api_url=self.api_url,
                                      username=self.username,
                                      password=self.password)
        self.assertEqual(success, True)
        self.assertEqual(type(pid_url), str)

        success, message = add_pid_checksum(pid_url=pid_url,
                                            checksum='BAR',
                                            username=self.username,
                                            password=self.password)
        self.assertEqual(success, True)
        self.assertEqual(type(message), str)

    def test_update_pid_nonexisting(self):
        success, message = add_pid_checksum(pid_url=self.api_url + '123',
                                            checksum='BAR',
                                            username=self.username,
                                            password=self.password)
        self.assertEqual(success, False)
        self.assertEqual(type(message), str)
