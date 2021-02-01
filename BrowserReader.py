import os
import json
import base64
import sqlite3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from win32crypt import CryptUnprotectData


class GoogleBrowerCookie:
    def __init__(self, host, type):
        self.host = host
        self.local_state = None
        self.cookie_path = None
        self.sql = "select host_key,name,encrypted_value from cookies where host_key='%s'" % host
        self.res = None
        self.cookies = dict()
        self.__init_reader(type)

    def __init_reader(self, type):
        if type == 'google':
            self.local_state = os.environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Local State'
            self.cookie_path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Cookies"
        elif type == 'edge':
            self.local_state = os.environ['LOCALAPPDATA'] + r'\Microsoft\Edge\User Data\Local State'
            self.cookie_path = os.environ['LOCALAPPDATA'] + r"\Microsoft\Edge\User Data\Default\Cookies"
        else:
            print("请输入正确的浏览器名称")
            exit(-1)

    def __get_string(self):
        with open(self.local_state, 'r', encoding='utf-8') as f:
            s = json.load(f)['os_crypt']['encrypted_key']
        return s

    def __pull_the_key(self, base64_encrypted_key):
        encrypted_key_with_header = base64.b64decode(base64_encrypted_key)
        encrypted_key = encrypted_key_with_header[5:]
        key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key

    def __decrypt_string(seelf, key, data):
        nonce, cipherbytes = data[3:15], data[15:]
        aesgcm = AESGCM(key)
        plainbytes = aesgcm.decrypt(nonce, cipherbytes, None)
        plaintext = plainbytes.decode('utf-8')
        return plaintext

    def get_cookie_from_chrome(self):
        with sqlite3.connect(self.cookie_path) as conn:
            cu = conn.cursor()
            self.res = cu.execute(self.sql).fetchall()
            cu.close()
            key = self.__pull_the_key(self.__get_string())
            for host_key, name, encrypted_value in self.res:
                if encrypted_value[0:3] == b'v10':
                    self.cookies[name] = self.__decrypt_string(key, encrypted_value)
                else:
                    self.cookies[name] = CryptUnprotectData(encrypted_value)[1].decode()

    def get_cookie_str(self):
        cookie_str = ''
        self.get_cookie_from_chrome()
        for i in self.cookies:
            cookie_str += i + "=" + self.cookies.get(i) + ";"

        return cookie_str
