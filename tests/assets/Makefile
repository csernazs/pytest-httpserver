

all: server.crt


rootCA.key:
	openssl genrsa -out rootCA.key 2048

rootCA.crt: rootCA.key rootCA.cnf
	openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 11083 -out rootCA.crt -config rootCA.cnf

server.csr server.key: server.cnf
	openssl req -new -sha256 -nodes -out server.csr -newkey rsa:2048 -keyout server.key -config server.cnf

server.crt: server.csr rootCA.crt rootCA.key v3.ext
	openssl x509 -req -in server.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out server.crt -days 11083 -sha256 -extfile v3.ext

clean:
	rm -f rootCA.key rootCA.crt server.csr server.key server.crt
