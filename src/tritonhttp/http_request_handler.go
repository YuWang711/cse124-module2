package tritonhttp

import (
	"net"
	"log"
//	"fmt"
	"io"
	"time"
//	"flag"
	"strings"
	"regexp"
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

	buf := make([]byte, 2048)
	var requestString string
	for {
		// Validate the request lines that were read
		conn.SetReadDeadline(time.Now().Add(timeoutDuration))
		//Double CRLF means the quest is ended
		// buf is unreadable somehow
		if _,err := conn.Read(buf); err == nil{
			requestString = requestString + string(buf)
			log.Println("request:", requestString)
			for strings.Contains(requestString, "\r\n\r\n") {
				request := strings.SplitN(requestString, "\r\n\r\n",2)
				var requestHeader HttpRequestHeader
				if strings.Contains(request[0], "\r\n") {
					split_request := strings.Split(request[0], "\r\n")
					checkRequest(split_request[0], &requestHeader)
					requestHeader.Header = make(map[string]string)
					for _,header := range split_request[1: len(split_request)] {
						if header != "" {
							addHeader(header, &requestHeader)
						}
					}
					if _, okay := requestHeader.Header["Host"]; !okay{
						requestHeader.Code = 400
						log.Println("this")
					}
					regex_string := "(\000)" + "{2,}"
					m1 := regexp.MustCompile(regex_string)
					new_string := m1.ReplaceAllString(request[1], "")
					requestString = new_string
					if requestHeader.Done != "Done" && requestHeader.Code == 200 {
						go func() {
							requestHeader.Done = hs.handleResponse(&requestHeader,conn)
						}()
					} else if requestHeader.Code == 400 {
						hs.handleBadRequest(conn)
						requestHeader.Done = "Done"
						return
					}
				}
			}
		} else	{
			if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
				if requestString != "" {
					hs.handleBadRequest(conn)
				}
				return
			} else if err == io.EOF {
				log.Println("Closed Connection Dectected")
				conn.Close()
				return
			}
		}

		//Finish sending response
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
	regex_string := "( )" + "{2,}"
	m1 := regexp.MustCompile(regex_string)
	new_string := m1.ReplaceAllString(str, " ")
	request_string := strings.Split(new_string, " ")
	//If missing one out of three content
	if len(request_string) < 3{
		requestHeader.Code = 400
		requestHeader.Done = "False"
		return
	}
	if request_string[0] == "GET" && request_string[2] == "HTTP/1.1"{
		if request_string[1][0] == '/' {
			if request_string[1][len(request_string[1])-1] == '/'{
				requestHeader.Request = request_string[1] + "index.html"
				requestHeader.Code = 200
				requestHeader.Done = "False"
			} else {
				requestHeader.Request = request_string[1]
				requestHeader.Code = 200
				requestHeader.Done = "False"
			}
		} else {
			requestHeader.Request= request_string[1]
			requestHeader.Code = 400
			requestHeader.Done = "False"
		}
	} else {
		requestHeader.Code = 400
		requestHeader.Done = "False"
	}
	return
}

func addHeader(str string, requestHeader *HttpRequestHeader){
	regex_string := "( )" + "{1,}"
	m1 := regexp.MustCompile(regex_string)
	new_str := m1.ReplaceAllString(str, "")
	if strings.Contains(new_str, ":"){
		header_string := strings.Split(new_str, ":")
		if len(header_string) == 2 {
			requestHeader.Header[header_string[0]] = header_string[1]
		}
	} else {
		requestHeader.Code = 400
	}
}
