#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>

#define DEFAULT_PORT 5000
#define BUFFER_SIZE 65536

int main(int argc, char *argv[]) {
    int port = DEFAULT_PORT;

    if (argc >= 2) {
        port = atoi(argv[1]);
    }

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

    if (sockfd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind");
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("UDP Server started on port %d\n", port);
    printf("Waiting for packets...\n");

    char buffer[BUFFER_SIZE];

    long packets = 0;
    long bytes = 0;

    time_t start = time(NULL);

    while (1) {
        ssize_t received = recvfrom(sockfd, buffer, sizeof(buffer), 0, NULL, NULL);

        if (received < 0) {
            perror("recvfrom");
            break;
        }

        packets++;
        bytes += received;

        time_t now = time(NULL);
        double duration = difftime(now, start);

        if (duration <= 0) {
            duration = 1;
        }

        double throughput_kbps = ((double)bytes * 8.0) / duration / 1000.0;

        printf("Packets: %ld | Bytes: %ld | Throughput: %.2f Kbit/s\r",
               packets,
               bytes,
               throughput_kbps);

        fflush(stdout);
    }

    close(sockfd);
    return EXIT_SUCCESS;
}