from typing import Tuple


def get_url_from_request(request):
        """Get the url from the decoded request
            :request - the request data received form the socket.
        """

        request_str = request.decode("utf-8")
        url_pos = request_str.find("Host:")
        return request_str[url_pos+5:].split("\n")[0]
    

def get_port_and_server(url: str) -> Tuple[int, str]:
    """Retrieve the port number and the webserver name from the url
        :url - the url from which the port and the server name to be obtained.
    """

    port = None
    webserver = None
    temp_url = url

    port_pos = temp_url.find(":")
    webserver_pos = temp_url.find("/")

    if webserver_pos == -1:
        webserver_pos = len(temp_url)
    
    if (port_pos == -1) or (webserver_pos < port_pos):
        port = 80
        webserver = temp_url[:webserver_pos]
    else:
        port = temp_url[port_pos+1: webserver_pos]
        webserver = temp_url[:port_pos]
    
    return int(port), webserver.strip()