#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <signal.h>
#include <stdint.h>

#define DEFAULT_PORT 5000
#define BUFFER_SIZE 65536
#define OUTPUT_FILE "udp_server_results.csv"

static volatile int running = 1;

void handle_signal(int signal) {
    (void)signal;
    running = 0;
}

int main(int argc, char *argv[]) {
    int port = DEFAULT_PORT;

    if (argc >= 2) {
        port = atoi(argv[1]);
    }

    signal(SIGINT, handle_signal);

    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    int opt = 1;

    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
    }

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

    FILE *csv = fopen(OUTPUT_FILE, "w");

    if (csv == NULL) {
        perror("fopen");
        close(sockfd);
        return EXIT_FAILURE;
    }

    fprintf(csv, "timestamp,sequence,packet_size,total_received,total_bytes,estimated_lost,loss_percent,throughput_kbps\n");

    printf("UDP Server started on port %d\n", port);
    printf("Saving results to %s\n", OUTPUT_FILE);
    printf("Press Ctrl+C to stop\n\n");

    char buffer[BUFFER_SIZE];

    uint64_t last_sequence = 0;
    uint64_t total_received = 0;
    uint64_t estimated_lost = 0;
    uint64_t bytes = 0;

    time_t start = time(NULL);

    while (running) {
        ssize_t received = recvfrom(sockfd, buffer, sizeof(buffer), 0, NULL, NULL);

        if (received < 0) {
            if (!running) {
                break;
            }

            perror("recvfrom");
            break;
        }

        if (received < (ssize_t)sizeof(uint64_t)) {
            continue;
        }

        uint64_t sequence_network;
        memcpy(&sequence_network, buffer, sizeof(sequence_network));
        uint64_t sequence = be64toh(sequence_network);

        total_received++;
        bytes += received;

        if (last_sequence > 0 && sequence > last_sequence + 1) {
            estimated_lost += sequence - last_sequence - 1;
        }

        if (sequence > last_sequence) {
            last_sequence = sequence;
        }

        uint64_t expected_total = total_received + estimated_lost;
        double loss_percent = expected_total > 0
            ? ((double)estimated_lost / (double)expected_total) * 100.0
            : 0.0;

        time_t now = time(NULL);
        double duration = difftime(now, start);

        if (duration <= 0) {
            duration = 1;
        }

        double throughput_kbps = ((double)bytes * 8.0) / duration / 1000.0;

        fprintf(csv, "%ld,%lu,%zd,%lu,%lu,%lu,%.2f,%.2f\n",
                now,
                sequence,
                received,
                total_received,
                bytes,
                estimated_lost,
                loss_percent,
                throughput_kbps);

        fflush(csv);

        printf("Seq: %lu | Received: %lu | Lost: %lu | Loss: %.2f%% | Throughput: %.2f Kbit/s\r",
               sequence,
               total_received,
               estimated_lost,
               loss_percent,
               throughput_kbps);

        fflush(stdout);
    }

    printf("\n\nServer stopped\n");
    printf("Total received: %lu\n", total_received);
    printf("Estimated lost: %lu\n", estimated_lost);
    printf("Total bytes: %lu\n", bytes);

    fclose(csv);
    close(sockfd);

    return EXIT_SUCCESS;
}