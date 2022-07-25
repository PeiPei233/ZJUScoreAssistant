import requests
import re
import math

class zjusess(requests.Session):
    def __rsa_no_padding__(self, src, modulus, exponent):
        m = int(modulus, 16)
        e = int(exponent, 16)
        t = bytes(src, 'ascii')
        # 字符串转换为bytes
        input_nr = int.from_bytes(t, byteorder='big')
        # 将字节转化成int型数字，如果没有标明进制，看做ascii码值
        crypt_nr = pow(input_nr, e, m)
        # 计算x的y次方，如果z在存在，则再对结果进行取模，其结果等效于pow(x,y) %z
        length = math.ceil(m.bit_length() / 8)
        # 取模数的比特长度(二进制长度)，除以8将比特转为字节
        crypt_data = crypt_nr.to_bytes(length, byteorder='big')
        # 将密文转换为bytes存储(8字节)，返回hex(16字节)
        return crypt_data.hex()
    
    def login(self, username, password):

        # 打开网站
        res = self.get(r'https://zjuam.zju.edu.cn/cas/login')
        # 获取execution的值以用于登录
        execution = re.findall(r'<input type="hidden" name="execution" value="(.*?)" />', res.text)[0]
        # 获取RSA公钥
        res = self.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey')
        modulus = res.json()['modulus']
        exponent = res.json()['exponent']

        rsapwd = self.__rsa_no_padding__(password, modulus, exponent)

        data = {
            'username': username,
            'password': rsapwd,
            'execution': execution,
            '_eventId': 'submit'
        }
        # 登录
        self.post(r'https://zjuam.zju.edu.cn/cas/login', data)