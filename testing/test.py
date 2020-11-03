from socket import socket
import unittest
import time
import sys
import concurrent.futures

server_address = "54.188.43.19"
server_port = 8080
BUFF_SIZE = 4096
Server = "Go-Triton-Server-YuWang"

#To Avoid Overloading server, some tests are commented out

def MapGoodMessage(received_message):
    str_msg = str(received_message, 'utf-8')
    Header_Content = str_msg.split("\r\n\r\n",1)
    Header = Header_Content[0]
    if(len(Header_Content)==2):
        Content = Header_Content[1]
    header_split = Header.split("\r\n",-1)
    result_dict = {}
    result_dict["Response"] = header_split[0]
    for header in header_split[1:]:
        new_header = header.replace(" ", "")
        split_header = new_header.split(":",1)
        if len(split_header) > 1:
            result_dict[split_header[0]] = (split_header[1])
    if(len(Header_Content)==2):
        result_dict["Contents"] = Content
    return result_dict

def MapHeader(Header):
    header_split = Header.split("\r\n",-1)
    result_dict = {}
    result_dict["Response"] = header_split 
    for header in header_split[1:]:
        new_header = header.replace(" ", "")
        split_header = new_header.split(":",1)
        if len(split_header) > 1:
            result_dict[split_header ] = split_header[1]
    return result_dict

def recvall(socket):
    data = b''
    while True:
        received = socket.recv(BUFF_SIZE)
        data += received
        if len(received) < BUFF_SIZE:
            break
    return data

def connectAndsendMessage(message):
        s = socket()
        s.connect((server_address, server_port))
        s.sendall(message)
        received_string = recvall(s)
        result_msg = MapGoodMessage(received_string)
        return result_msg,s

def connect():
    s = socket()
    s.connect((server_address, server_port))
    return s

def sendMessage(message,s):
    s.sendall(message)
    received_string = recvall(s)
    result_msg = MapGoodMessage(received_string)
    return result_msg

def connectAndsendMessageJPG(message):
        s = socket()
        s.connect((server_address, server_port))
        s.sendall(message)
        received_string = recvall(s)
        Header = ""
        Content = b''
        for i in range(len(received_string)):
            new_char = chr(received_string[i])
            if new_char == '\r':
                new_char = chr(received_string[i+1])
                if new_char == '\n':
                    new_char = chr(received_string[i+2])
                    if new_char == '\r':
                        new_char = chr(received_string[i+3])
                        if new_char == '\n':
                            Header = str(received_string[:i], 'utf-8')
                            Content = received_string[i+4:]
                            break
        result_dict =  MapHeader(Header)
        result_dict["Contents"] = Content
        return result_dict,s


class TestSocket(unittest.TestCase):

    #Basic Functions 200 code response
    def test_Good_Default_Path_Test(self):
        result_msg,s = connectAndsendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
        self.assertEqual(result_msg ["Server"] ,  Server)
        self.assertEqual(result_msg ["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg ["Content-Type"] , "text/html")
        self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s.close()
    def test_Good_Subdirectory_Default_Path(self):
        result_msg,s = connectAndsendMessage(b"GET /subdir1/ HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
        self.assertEqual(result_msg ["Server"] ,  Server)
        self.assertEqual(result_msg ["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg ["Content-Type"] , "text/html")
        self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s.close()
    def test_Good_Empty(self):
        result_msg,s = connectAndsendMessage(b"GET /sample.txt HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
        self.assertEqual(result_msg ["Server"] ,  Server)
        self.assertEqual(result_msg ["Last-Modified"] , "2020-11-0122:41:26.337030167+0000UTC")
        self.assertEqual(result_msg ["Content-Type"] , "text/plain")
        self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s.close()
    def test_Jpeg_Image(self):
        result_msg,s = connectAndsendMessageJPG(b"GET /kitten.jpg HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
        self.assertEqual(result_msg ["Server"] ,  Server)
        self.assertEqual(result_msg ["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg ["Content-Type"] , "image/jpeg")
        self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s.close()
    def test_nested_directory(self):
        result_msg,s = connectAndsendMessage(b"GET /subdir1/subdir11/ HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
        self.assertEqual(result_msg ["Server"] ,  Server)
        self.assertEqual(result_msg ["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg ["Content-Type"] , "text/html")
        self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s.close()
    def test_PNG_Image(self):
        result_msg,s = connectAndsendMessageJPG(b"GET /UCSD_Seal.png HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
        self.assertEqual(result_msg ["Server"] ,  Server)
        self.assertEqual(result_msg ["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg ["Content-Type"] , "image/png")
        self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s.close()
    def test_Good_Relative_Path(self):
        result_msg,s = connectAndsendMessage(b"GET /../sample_htdocs/ HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
        self.assertEqual(result_msg ["Server"] ,  Server)
        self.assertEqual(result_msg ["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg ["Content-Type"] , "text/html")
        self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s.close()
    def test_Large_Request(self):
        result_msg,s = connectAndsendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 200" in result_msg ["Response"])
        self.assertEqual(result_msg ["Server"],  Server)
        self.assertEqual(result_msg ["Last-Modified"], "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg ["Content-Type"], "text/html")
        self.assertEqual(int(result_msg ["Content-Length"]),len(result_msg["Contents"]))
        s.close()
    #Basic non-200 error code
    def test_File_Not_Found(self):
        result_msg,s = connectAndsendMessage(b"GET /dafkjd.txt HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 404" in result_msg ["Response"] )
        s.close()
    def test_Malformed_URL(self):
        result_msg,s = connectAndsendMessage(b"GET dafkjd.txt HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 400" in result_msg ["Response"] )
        s.close()
    def test_Host_Header_Missing(self):
        result_msg,s = connectAndsendMessage(b"GET / HTTP/1.1\r\n\r\n")
        self.assertTrue("HTTP/1.1 400" in result_msg ["Response"] )
        s.close()
    def test_Error_GETT(self):
        result_msg,s = connectAndsendMessage(b"GETT / HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 400" in result_msg ["Response"] )
        s.close()
    def test_Path_Escaping(self):
        result_msg,s = connectAndsendMessage(b"GET ../ HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 400" in result_msg ["Response"] )
        s.close()
    def test_File_Not_Found_Subdirectory(self):
        result_msg,s = connectAndsendMessage(b"GET /subdir1/blah.txt HTTP/1.1\r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 404" in result_msg ["Response"] )
        s.close()
    def test_Malformed_Header_Test(self):
        result_msg,s = connectAndsendMessage(b"GET /subdir1/ HTTP/1.1\r\nHost: HA\r\nblah\r\n\r\n")
        self.assertTrue("HTTP/1.1 400" in result_msg ["Response"] )
        s.close()
    def test_HTTP_Missing(self):
        result_msg,s = connectAndsendMessage(b"GET / \r\nHost: HA\r\n\r\n")
        self.assertTrue("HTTP/1.1 400" in result_msg ["Response"] )
        s.close()
    def test_Partial_Request_Timeout(self):
        result_msg,s = connectAndsendMessage(b"GET /subdir1/blah.txt HTTP/1.1\r\nHost: HA\r\n")
        time.sleep(5)
        self.assertTrue("HTTP/1.1 400" in result_msg ["Response"] )
        s.close()
    #Concurrency
    def test_Concurrency(self):
        s1 = connect()
        s2 = connect()
        args = [[b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s1], [b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s2]]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            for result_msg in executor.map(lambda p: sendMessage(*p),args):
                self.assertTrue("HTTP/1.1 200" in result_msg ["Response"] )
                self.assertEqual(result_msg ["Server"] ,  Server)
                self.assertEqual(result_msg ["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
                self.assertEqual(result_msg ["Content-Type"] , "text/html")
                self.assertEqual(int(result_msg ["Content-Length"] ),len(result_msg ["Contents"] ))
        s1.close()
        s2.close()

    # Pipelining
    def test_Pipeline_Request(self):
        result_msg = []
        result_recent,s = connectAndsendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n")
        result_msg.append(result_recent)
        result_recent,s = connectAndsendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n")
        result_msg.append(result_recent)
        result_recent,s = connectAndsendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n")
        result_msg.append(result_recent)
        for i in range(len(result_msg)):
            self.assertTrue("HTTP/1.1 200" in result_msg[i]["Response"])
            self.assertEqual(result_msg[i]["Server"],  Server)
            self.assertEqual(result_msg[i]["Last-Modified"], "2020-10-2823:40:19.022470984+0000UTC")
            self.assertEqual(result_msg[i]["Content-Type"], "text/html")
            self.assertEqual(int(result_msg[i]["Content-Length"]),len(result_msg[i]["Contents"]))
        s.close()
    def test_Pipeline_with_404_Request(self):
        s = connect()
        result_msg_1 = sendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s)
        result_msg_2 = sendMessage(b"GET /dontexist.txt HTTP/1.1\r\nHost: HA\r\n\r\n",s)
        result_msg_3 = sendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s)
        args = [b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s]
        self.assertTrue("HTTP/1.1 200" in result_msg_1["Response"] )
        self.assertEqual(result_msg_1["Server"] ,  Server)
        self.assertEqual(result_msg_1["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg_1["Content-Type"] , "text/html")
        self.assertEqual(int(result_msg_1["Content-Length"] ),len(result_msg_1["Contents"] ))
        self.assertTrue("HTTP/1.1 404" in result_msg_2["Response"] )
        self.assertTrue(not bool(result_msg_3["Response"]))
        s.close()
    def test_Pipeline_with_400_Request(self):
        s = connect()
        result_msg_1 = sendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s)
        print(result_msg_1)
        result_msg_2 = sendMessage(b"GET asdf HTTP/1.1\r\nHost: HA\r\n\r\n",s)
        result_msg_3 = sendMessage(b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s)
        args = [b"GET / HTTP/1.1\r\nHost: HA\r\n\r\n",s]
        self.assertTrue("HTTP/1.1 200" in result_msg_1["Response"] )
        self.assertEqual(result_msg_1["Server"] ,  Server)
        self.assertEqual(result_msg_1["Last-Modified"] , "2020-10-2823:40:19.022470984+0000UTC")
        self.assertEqual(result_msg_1["Content-Type"] , "text/html")
        self.assertEqual(int(result_msg_1["Content-Length"] ),len(result_msg_1["Contents"] ))
        self.assertTrue("HTTP/1.1 400" in result_msg_2["Response"] )
        self.assertTrue(not bool(result_msg_3["Response"]))
        s.close()


def main(out = sys.stderr, verbosity = 2): 
    loader = unittest.TestLoader() 
  
    suite = loader.loadTestsFromModule(sys.modules[__name__]) 
    unittest.TextTestRunner(out, verbosity = verbosity).run(suite) 
      
if __name__ == '__main__': 
    with open('output.txt', 'w') as f: 
        main(f) 