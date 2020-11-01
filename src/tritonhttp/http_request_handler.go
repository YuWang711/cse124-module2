package tritonhttp

import (
	"net"
	"log"
//	"fmt"
	"io"
	"time"
//	"flag"
	"strings"
)

/* 
For a connection, keep handling requests until 
	1. a timeout occurs or
	2. client closes connection or
	3. client sends a bad request
*/
func (hs *HttpServer) handleConnection(conn net.Conn) {
	log.Println("Accepted new Connection")
	//client closes connection
	defer conn.Close()
	defer log.Println("Closed connection.")

	timeoutDuration := 5 * time.Second
	// Start a loop for reading requests continuously

	buf := make([]byte, 1024)
	var requestHeaderArray []HttpRequestHeader
	//c := bufio.NewReader(conn)
	for {
		// Validate the request lines that were read
		conn.SetReadDeadline(time.Now().Add(timeoutDuration))
		//Double CRLF means the quest is ended
		// buf is unreadable somehow
		if size,err := conn.Read(buf); err == nil{
			var requestHeader HttpRequestHeader
			requestString := string(buf)
			log.Println("request:", requestString)
			log.Println("size:", size)
			split_request := strings.Split(requestString, "\r\n")
			checkRequest(split_request[0], &requestHeader)
			requestHeader.Header = make(map[string]string)
			for _,header := range split_request[1:] {
				if header != "" {
					addHeader(header, &requestHeader)
				}
			}
			if requestHeader.Header["Host"] == "" || requestHeader.Code == 400{
				hs.handleBadRequest(conn)
				requestHeader.Done = "True"
			} else {
				requestHeaderArray = append(requestHeaderArray, requestHeader)
			}
		} else	{
			if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
				log.Println("read timeout:", err)
				if len(requestHeaderArray) < 1 {
					hs.handleBadRequest(conn)
					return
				}
			} else if err == io.EOF {
				log.Println("Closed Connection Dectected")
				for len(requestHeaderArray) > 0{
					//Finish sending response
				}
				conn.Close()
				return
			}
			log.Println("read error:", err)
		}

		for i,Request := range requestHeaderArray[:]{
			//Finish sending response
			go func() {
				Request.Done = hs.handleResponse(&Request,conn)
				if Request.Done == "Done"{
					requestHeaderArray = append(requestHeaderArray[:i], requestHeaderArray[i+1:]...)
				}
			}()
		}
		// Handle any complete requests
		//if timeout occurs
		// Set a timeout for read operation
		//client sends a bad request
	}
	// Read from the connection socket into a buffer
	// Update any ongoing requests
	// If reusing read buffer, truncate it before next read
}

func checkRequest(str string, requestHeader *HttpRequestHeader) {
	request_string := strings.Split(str, " ")
	if len(request_string) < 3{
		requestHeader.Code = 400
		requestHeader.Done = "False"
		return
	}
	if request_string[0] == "GET" && request_string[2] == "HTTP/1.1"{
		log.Println("GET CHECKED")
		if request_string[1][len(request_string[1])-1] == '/'{
			requestHeader.Request = "/index.html"
			requestHeader.Code = 200
			requestHeader.Done = "False"
		} else {
			if request_string[1][0] == '/' {
				requestHeader.Request = request_string[1]
				requestHeader.Code = 200
				requestHeader.Done = "False"
			} else {
				requestHeader.Request= request_string[1]
				requestHeader.Code = 400
				requestHeader.Done = "False"
			}
		}
		return
	} else {
		requestHeader.Code = 400
		requestHeader.Done = "False"
		return
	}
}

func addHeader(str string, requestHeader *HttpRequestHeader){
	new_str := strings.Replace(str, " ", "", -1)
	header_string := strings.Split(new_str, ":")
	log.Println(header_string)
	if len(header_string) > 1 {
		requestHeader.Header[header_string[0]] = header_string[1]
	}
}
