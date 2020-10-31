package tritonhttp

import (
	"log"
	"os"
	"bufio"
	"strings"
	"net"
	//"strconv"
	//"flag"
)
/** 
	Initialize the tritonhttp server by populating HttpServer structure
**/
func NewHttpdServer(port, docRoot, mimePath string) (*HttpServer, error) {

	// Initialize mimeMap for server to refer
	var tritonhttp HttpServer
	file,err := os.Open("./src/mime.types")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	tritonhttp.MIMEMap = make(map[string]string)

	for scanner.Scan(){
		s := scanner.Text()
		ss := strings.Fields(s)
		extension := ss[0]
		file_type := ss[1]
		tritonhttp.MIMEMap[extension] = file_type
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
	// Return pointer to HttpServer
	return &tritonhttp, err
}

/** 
	Start the tritonhttp server
**/
func (hs *HttpServer) Start() (err error) {
	// Start listening to the server port
	log.Println("starting server")
	//port := flag.Int("port", 3333, "Port to accept connections on.")
	//host := flag.String("host", "127.0.0.1", "Host or IP to bind to")

	listen, err := net.Listen("tcp", ":8080")

	if err != nil {
		log.Panicln(err)
	}

	for{
		// Accept connection from client
		conn,err := listen.Accept()
		if err != nil {
			log.Panicln(err)
		}
		// Need to establish connection with client
		// Spawn a go routine to handle request
		go hs.handleConnection(conn)
	}

}


