CC=gcc
CFLAGS=-Wall -Wextra -O2
TARGET=emulator
SRC=src/main.c

all:
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

run: all
	./$(TARGET)

clean:
	rm -f $(TARGET)