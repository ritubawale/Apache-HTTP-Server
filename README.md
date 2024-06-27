# Apache-HTTP-Server
# Python HTTP Server

This project is a simple HTTP server implemented in Python 3. It can handle various HTTP methods such as GET, POST, PUT, DELETE, HEAD, and OPTIONS. The server supports conditional GET requests and logs errors.

## Features

- Handle HTTP methods: GET, POST, PUT, DELETE, HEAD, and OPTIONS
- Parse and store GET and POST parameters in CSV files
- Conditional GET requests
- Error handling for common HTTP errors
- Multithreading to handle multiple client connections

## Requirements

- Python 3.x

## Usage

### Running the Server

1. Ensure you have Python 3 installed on your machine.
2. Clone the repository and navigate to the project directory.
3. Update the `dev.conf` configuration file with your settings.
4. Run the server using the following command:

```sh
python3 HttpServer.py dev.conf

