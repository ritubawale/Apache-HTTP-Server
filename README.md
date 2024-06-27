```markdown
# Apache HTTP Server

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
python3 server.py
```

### Configuration

The server configuration is stored in the `dev.conf` file. Here is an example configuration:

```
adminFlag 0
MaxKeepAliveRequests 10
serverRoot /path/to/server/root
ErrorLog /path/to/error_log
```

### Making Requests

You can use `curl` to test the server. Below are some example `curl` commands for different HTTP methods:

#### GET Request

```sh
curl -X GET http://localhost:8080/path/to/resource
```

#### POST Request

```sh
curl -X POST http://localhost:8080/path/to/resource -d "param1=value1&param2=value2"
```

#### PUT Request

```sh
curl -X PUT http://localhost:8080/path/to/resource --data-binary @file_to_upload.txt
```

#### DELETE Request

```sh
curl -X DELETE http://localhost:8080/path/to/resource
```

#### OPTIONS Request

```sh
curl -X OPTIONS http://localhost:8080/path/to/resource
```

#### HEAD Request

```sh
curl -X HEAD http://localhost:8080/path/to/resource
```

## Error Handling

The server handles the following HTTP errors:
- 400: Bad Request
- 403: Forbidden
- 404: Not Found
- 405: Method Not Allowed
- 501: Method Not Implemented

Error responses are logged in the `error_log` file specified in the configuration.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.
