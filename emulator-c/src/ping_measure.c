#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define OUTPUT_FILE "ping_results.csv"
#define DEFAULT_HOST "8.8.8.8"
#define DEFAULT_COUNT 10

static int run_ping(const char *host, double *latency_ms) {
    char command[256];
    char buffer[1024];

    snprintf(command, sizeof(command),
             "ping -c 1 -W 2 %s | grep 'time='", host);

    FILE *pipe = popen(command, "r");

    if (pipe == NULL) {
        return 0;
    }

    int success = 0;

    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        char *time_ptr = strstr(buffer, "time=");

        if (time_ptr != NULL) {
            *latency_ms = atof(time_ptr + 5);
            success = 1;
            break;
        }
    }

    pclose(pipe);
    return success;
}

int main(int argc, char *argv[]) {
    const char *host = DEFAULT_HOST;
    int count = DEFAULT_COUNT;

    if (argc >= 2) {
        host = argv[1];
    }

    if (argc >= 3) {
        count = atoi(argv[2]);
        if (count <= 0) {
            count = DEFAULT_COUNT;
        }
    }

    FILE *fp = fopen(OUTPUT_FILE, "w");

    if (fp == NULL) {
        perror("Cannot create CSV file");
        return EXIT_FAILURE;
    }

    fprintf(fp, "timestamp,host,sequence,status,latency_ms\n");

    int received = 0;
    double sum_latency = 0.0;
    double previous_latency = -1.0;
    double jitter_sum = 0.0;
    int jitter_samples = 0;

    printf("5G Network Measurement Module\n");
    printf("Target host: %s\n", host);
    printf("Measurements: %d\n\n", count);

    for (int i = 1; i <= count; i++) {
        double latency = 0.0;
        time_t now = time(NULL);

        int ok = run_ping(host, &latency);

        if (ok) {
            received++;
            sum_latency += latency;

            if (previous_latency >= 0.0) {
                double diff = latency - previous_latency;

                if (diff < 0) {
                    diff = -diff;
                }

                jitter_sum += diff;
                jitter_samples++;
            }

            previous_latency = latency;

            fprintf(fp, "%ld,%s,%d,OK,%.2f\n",
                    now, host, i, latency);

            printf("[%d/%d] OK %.2f ms\n", i, count, latency);
        } else {
            fprintf(fp, "%ld,%s,%d,LOST,0\n",
                    now, host, i);

            printf("[%d/%d] LOST\n", i, count);
        }

        sleep(1);
    }

    double packet_loss = ((double)(count - received) / count) * 100.0;
    double avg_latency = received > 0 ? sum_latency / received : 0.0;
    double avg_jitter = jitter_samples > 0 ? jitter_sum / jitter_samples : 0.0;

    printf("\nResults:\n");
    printf("Sent: %d\n", count);
    printf("Received: %d\n", received);
    printf("Packet loss: %.2f %%\n", packet_loss);
    printf("Average latency: %.2f ms\n", avg_latency);
    printf("Average jitter: %.2f ms\n", avg_jitter);

    fprintf(fp, "\nsummary,,,,\n");
    fprintf(fp, "sent,%d,,,\n", count);
    fprintf(fp, "received,%d,,,\n", received);
    fprintf(fp, "packet_loss_percent,%.2f,,,\n", packet_loss);
    fprintf(fp, "average_latency_ms,%.2f,,,\n", avg_latency);
    fprintf(fp, "average_jitter_ms,%.2f,,,\n", avg_jitter);

    fclose(fp);

    printf("\nResults saved to %s\n", OUTPUT_FILE);

    return EXIT_SUCCESS;
}