#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(int argc, char *argv[]) {
    printf("5G Network Emulator C Module\n");
    printf("Traffic and metrics module started\n");

    time_t now = time(NULL);
    printf("Started at: %s", ctime(&now));

    return 0;
}