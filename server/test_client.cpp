#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>

#define BUF_SIZ 4096

int send_request(const int sock, const char *hostname)
{
    char request[BUF_SIZ];

    snprintf(request, sizeof(request), "GET / HTTP/1.1\r\n"
        "Host: %s\r\n"
        "Connection: Close\r\n\r\n", hostname);

    if (send(sock, request, strlen(request), 0) == -1)
    {
        perror("send() failed");
        return 1;
    }

    return 0;
}

int view_response(const int sock)
{
    char response[BUF_SIZ];
    int bytes;

    while((bytes = recv(sock, response, sizeof(response), 0)) > 0)
        fwrite(response, 1, bytes, stdout);

    if (bytes < 0)
    {
        perror("recv() failed");
        return 1;
    }

    return 0;
}

int main(int argc, char *argv[])
{
    struct hostent *host;
    struct sockaddr_in addr;
    int s;

    if (argc < 2)
    {
        fprintf(stderr, "usage: %s <host>\n", argv[0]);
        return 1;
    }

    if (!inet_aton(argv[1], &addr.sin_addr))
    {
        host = gethostbyname(argv[1]);
        if (!host)
        {
            herror("gethostbyname() failed");
            return 2;
        }
        addr.sin_addr = *(struct in_addr*)host->h_addr;
    }

    s = socket(PF_INET, SOCK_STREAM, 0);
    if (s == -1)
    {
        perror("socket() failed");
        return 3;
    }

    printf("connecting to %s:80...", inet_ntoa(addr.sin_addr));
    fflush(stdout);

    addr.sin_port = htons(50007);
    addr.sin_family = AF_INET;

    if (connect(s, (struct sockaddr*)&addr, sizeof(addr)) == -1)
    {
        perror("connect() failed");
        return 4;
    }

    puts("ok.");

    if (send_request(s, argv[1]))
        return 5;

    if (view_response(s))
        return 6;

    close(s);

    return 0;
}
