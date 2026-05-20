#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define OUTPUT_FILE "ping_results.csv"

int main() {
    FILE *fp;
    char command[256];
    char buffer[1024];

    printf("5G Network Measurement Module\n");

    fp = fopen(OUTPUT_FILE, "w");

    if (fp == NULL) {
        perror("Cannot create CSV file");
        return EXIT_FAILURE;
    }

    fprintf(fp, "timestamp,host,latency_ms\n");

    const char *host = "8.8.8.8";

    snprintf(command, sizeof(command),
             "ping -c 1 %s | grep 'time='", host);

    FILE *ping_pipe = popen(command, "r");

    if (ping_pipe == NULL) {
        perror("Ping failed");
        fclose(fp);
        return EXIT_FAILURE;
    }

    while (fgets(buffer, sizeof(buffer), ping_pipe) != NULL) {

        char *time_ptr = strstr(buffer, "time=");

        if (time_ptr != NULL) {

            double latency = atof(time_ptr + 5);

            time_t now = time(NULL);

            fprintf(fp, "%ld,%s,%.2f\n",
                    now,
                    host,
                    latency);

            printf("Latency to %s: %.2f ms\n",
                   host,
                   latency);
        }
    }

    pclose(ping_pipe);
    fclose(fp);

    printf("Results saved to %s\n", OUTPUT_FILE);

    return EXIT_SUCCESS;
}