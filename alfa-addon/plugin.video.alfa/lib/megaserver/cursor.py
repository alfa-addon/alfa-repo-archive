import urllib2
from Crypto.Cipher import AES
from Crypto.Util import Counter

class Cursor(object):
    def __init__(self, file):
        self._file=file
        self.pos=0
        self.conn =None
        self.initial_value = file.initial_value
        self.k = file.k

    def mega_request(self,offset, retry=False):
        if not self._file.url or retry:
            if self._file.folder_id :
                file = self._file._client.api_req({"a":"g","g":1,"n":self._file.file_id},"&n="+self._file.folder_id)
                self._file.url= file["g"]
            else:
                file = self._file._client.api_req({'a': 'g', 'g': 1, 'p': self._file.file_id})
                self._file.url= file["g"]

        req = urllib2.Request(self._file.url)
        req.headers['Range'] = 'bytes=%s-' % (offset)
        try:
            self.conn = urllib2.urlopen(req)
            self.prepare_decoder(offset)
        except:
            #La url del archivo expira transcurrido un tiempo, si da error 403, reintenta volviendo a solicitar la url mediante la API
            self.mega_request(offset, True)

    def read(self,n=None):
        if not self.conn:
            return
        res=self.conn.read(n)
        if res:
            res = self.decode(res)
            self.pos+=len(res)
        return res


    def seek(self,n):
        if n>self._file.size:
            n=self._file.size
        elif n<0:
            raise ValueError('Seeking negative')
        self.mega_request(n)
        self.pos=n

    def tell(self):
        return self.pos

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_val, exc_tb):
        self._file.cursors.remove(self)
        if len(self._file.cursors) == 0: self._file.cursor = False
        
    def decode(self, data):
        return self.decryptor.decrypt(data)

    def prepare_decoder(self,offset):
        initial_value = self.initial_value + int(offset/16)
        self.decryptor = AES.new(self._file._client.a32_to_str(self.k), AES.MODE_CTR, counter = Counter.new(128, initial_value = initial_value))
        #self.decryptor = aes.AESModeOfOperationCTR(f=self,key=self._client.a32_to_str(self.k),counter=aes.Counter(initial_value=initial_value))
        rest = offset - int(offset/16)*16
        if rest:
            self.decode(str(0)*rest)