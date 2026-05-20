CC=gcc
CFLAGS=-Wall -Wextra -O2

TARGET=ping_measure

SRC=src/ping_measure.c

all:
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

run: all
	./$(TARGET)

clean:
	rm -f $(TARGET)
	rm -f *.csv