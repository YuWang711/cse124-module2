package tritonhttp


type HttpServer	struct {
	ServerPort	string
	DocRoot		string
	MIMEPath	string
	MIMEMap		map[string]string
}

type HttpResponseHeader struct {
	// Add any fields required for the response here
	Request		string
	Server		string
	Last_Modified	string
	Content_Type	string
	Content_Length	int64
}
type HttpRequestHeader struct {
	// Add any fields required for the request here
	Request		string
	Header		map[string]string
	Code		int
	Done		string
	ResponseHeader	HttpResponseHeader
}
