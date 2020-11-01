package tritonhttp

import (
	"net"
	"log"
	"os"
	"strconv"
	"strings"
	"bufio"
)

func (hs *HttpServer) handleBadRequest(conn net.Conn) {
	log.Println("400! Bad Request")
	response_String := "HTTP/1.1 400 BadRequest\r\nServer: Go-Triton-Server\r\n\r\n"
	response_Byte := []byte(response_String)
	_,err := conn.Write(response_Byte)
	if err != nil {
		log.Println("error: ", err)
	}
}

func (hs *HttpServer) handleFileNotFoundRequest(requestHeader *HttpRequestHeader, conn net.Conn) {
	log.Println("404! Not Found")
	response_String := "HTTP/1.1 404 File Not Found\r\nServer: Go-Triton-Server\r\n\r\n"
	response_Byte := []byte(response_String)
	_,err := conn.Write(response_Byte)
	if err != nil {
		log.Println("error: ", err)
	}
}

func (hs *HttpServer) handleResponse(requestHeader *HttpRequestHeader, conn net.Conn) (result string) {
	log.Println("Request was success")
	//Create a response header, then record the size that we had send so far.
	var responseHeader HttpResponseHeader

	filename := hs.DocRoot+requestHeader.Request
	if file,err:= os.Stat(filename);err == nil{
		requestHeader.ResponseHeader = responseHeader
		responseHeader.Request = requestHeader.Request
		log.Println(requestHeader.Request)
		responseHeader.Server =  "Go-Triton-Server"
		responseHeader.Last_Modified = file.ModTime().String()
		responseHeader.Content_Length = file.Size()
		hs.sendResponse(responseHeader, conn)
	} else if os.IsNotExist(err){
		hs.handleFileNotFoundRequest(requestHeader, conn)
	} else if err != nil && !os.IsNotExist(err){
	//Calls file not found if file not found
		log.Println(err)
	}
	//Not sure what we are sending back?
	return "Done"
}

func (hs *HttpServer) sendResponse(responseHeader HttpResponseHeader, conn net.Conn) {

	file,err := os.Open(hs.DocRoot+responseHeader.Request)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	s := bufio.NewScanner(file)
	log.Println("Content Length: ", responseHeader.Content_Length)
	// Send headers
	response_String := "HTTP/1.1 200 " + responseHeader.Request + "\r\n"
	response_String = response_String + "Server: " + responseHeader.Server + "\r\n"
	response_String = response_String + "Last-Modified: " + responseHeader.Last_Modified + "\r\n"
	response_String = response_String + "Content-Length: " +  strconv.FormatInt(responseHeader.Content_Length,10) + "\r\n"
	split_data_type := strings.Split(responseHeader.Request, ".")
	response_String = response_String + "Content-Type: " + hs.MIMEMap["."+split_data_type[1]] + "\r\n\r\n"
	// Send file if required
	response_Byte := []byte(response_String)
	_,err = conn.Write(response_Byte)
	if err != nil {
		log.Println("error: ", err)
	}
	for s.Scan(){
		line := s.Text()
		line_byte := []byte(line)
		_,err := conn.Write(line_byte)
		if err != nil {
			return
		}
	}
	// Hint - Use the bufio package to write response
}
