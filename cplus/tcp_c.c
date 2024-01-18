#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>

int main(int argc, char *argv[])
{
	int fd = socket(AF_INET, SOCK_STREAM, 0);
	if (fd < 0) return -1;

	char ip_str[16] = "127.0.0.1";
	if (argc > 1)
		strncpy(ip_str, argv[1], strlen(argv[1]));

	struct sockaddr_in client_in = {
		.sin_addr.s_addr = inet_addr(ip_str),
		.sin_port = htons(1234),
		.sin_family = AF_INET,
	};

	char buf[64] = {0};

	int ret = connect(fd, (struct sockaddr *)&client_in, sizeof(client_in));
	if (!ret) {
		recv(fd, &buf, sizeof(buf), 0);
		printf("recive: %s\n", buf);
		strcpy(buf, "Hello, This is TCP client");
		send(fd, buf, strlen(buf), 0);
	}

	close(fd);

	return EXIT_SUCCESS;
}
