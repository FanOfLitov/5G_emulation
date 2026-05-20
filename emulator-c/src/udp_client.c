#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>

#define DEFAULT_SERVER_IP "127.0.0.1"
#define DEFAULT_PORT 5000
#define DEFAULT_PACKETS 100
#define DEFAULT_PAYLOAD_SIZE 512

int main(int argc, char *argv[]) {
    const char *server_ip = DEFAULT_SERVER_IP;
    int port = DEFAULT_PORT;
    int packets = DEFAULT_PACKETS;
    int payload_size = DEFAULT_PAYLOAD_SIZE;

    if (argc >= 2) server_ip = argv[1];
    if (argc >= 3) port = atoi(argv[2]);
    if (argc >= 4) packets = atoi(argv[3]);
    if (argc >= 5) payload_size = atoi(argv[4]);

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

    if (sockfd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, server_ip, &server_addr.sin_addr) <= 0) {
        perror("inet_pton");
        close(sockfd);
        return EXIT_FAILURE;
    }

    char *payload = malloc(payload_size);

    if (payload == NULL) {
        perror("malloc");
        close(sockfd);
        return EXIT_FAILURE;
    }

    memset(payload, 'A', payload_size);

    printf("UDP Traffic Generator\n");
    printf("Target: %s:%d\n", server_ip, port);
    printf("Packets: %d\n", packets);
    printf("Payload size: %d bytes\n\n", payload_size);

    time_t start = time(NULL);

    for (int i = 1; i <= packets; i++) {
        ssize_t sent = sendto(sockfd,
                              payload,
                              payload_size,
                              0,
                              (struct sockaddr *)&server_addr,
                              sizeof(server_addr));

        if (sent < 0) {
            perror("sendto");
            free(payload);
            close(sockfd);
            return EXIT_FAILURE;
        }

        printf("[%d/%d] sent %zd bytes\n", i, packets, sent);
        usleep(100000);
    }

    time_t end = time(NULL);
    double duration = difftime(end, start);

    if (duration <= 0) {
        duration = 1;
    }

    double total_bits = (double)packets * payload_size * 8;
    double bitrate_kbps = total_bits / duration / 1000.0;

    printf("\nResults:\n");
    printf("Total sent: %.0f bytes\n", (double)packets * payload_size);
    printf("Duration: %.2f sec\n", duration);
    printf("Approx bitrate: %.2f Kbit/s\n", bitrate_kbps);

    free(payload);
    close(sockfd);

    return EXIT_SUCCESS;
}