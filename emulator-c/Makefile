CC=gcc
CFLAGS=-Wall -Wextra -O2

PING_TARGET=ping_measure
UDP_CLIENT_TARGET=udp_client

PING_SRC=src/ping_measure.c
UDP_CLIENT_SRC=src/udp_client.c

all: $(PING_TARGET) $(UDP_CLIENT_TARGET)

$(PING_TARGET): $(PING_SRC)
	$(CC) $(CFLAGS) $(PING_SRC) -o $(PING_TARGET)

$(UDP_CLIENT_TARGET): $(UDP_CLIENT_SRC)
	$(CC) $(CFLAGS) $(UDP_CLIENT_SRC) -o $(UDP_CLIENT_TARGET)

run: $(PING_TARGET)
	./$(PING_TARGET)

run-udp: $(UDP_CLIENT_TARGET)
	./$(UDP_CLIENT_TARGET)

clean:
	rm -f $(PING_TARGET)
	rm -f $(UDP_CLIENT_TARGET)
	rm -f *.csv