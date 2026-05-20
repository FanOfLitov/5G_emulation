CC=gcc
CFLAGS=-Wall -Wextra -O2

PING_TARGET=ping_measure
UDP_CLIENT_TARGET=udp_client
UDP_SERVER_TARGET=udp_server

PING_SRC=src/ping_measure.c
UDP_CLIENT_SRC=src/udp_client.c
UDP_SERVER_SRC=src/udp_server.c

all: $(PING_TARGET) $(UDP_CLIENT_TARGET) $(UDP_SERVER_TARGET)

$(PING_TARGET): $(PING_SRC)
	$(CC) $(CFLAGS) $(PING_SRC) -o $(PING_TARGET)

$(UDP_CLIENT_TARGET): $(UDP_CLIENT_SRC)
	$(CC) $(CFLAGS) $(UDP_CLIENT_SRC) -o $(UDP_CLIENT_TARGET)

$(UDP_SERVER_TARGET): $(UDP_SERVER_SRC)
	$(CC) $(CFLAGS) $(UDP_SERVER_SRC) -o $(UDP_SERVER_TARGET)

run: $(PING_TARGET)
	./$(PING_TARGET)

run-udp-client: $(UDP_CLIENT_TARGET)
	./$(UDP_CLIENT_TARGET)

run-udp-server: $(UDP_SERVER_TARGET)
	./$(UDP_SERVER_TARGET)

clean:
	rm -f $(PING_TARGET)
	rm -f $(UDP_CLIENT_TARGET)
	rm -f $(UDP_SERVER_TARGET)
	rm -f *.csv