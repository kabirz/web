#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
	char buf[64] = {0};
	int fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd < 0) return -1;

	char ip_str[16] = "127.0.0.1";
	if (argc > 1)
		strncpy(ip_str, argv[1], strlen(argv[1]));
	struct sockaddr_in ssi = {
		.sin_addr.s_addr = inet_addr(ip_str),
		.sin_port = htons(5678),
		.sin_family = AF_INET,
	};

	for (int i = 0; i < 10; i++) {
		snprintf(buf, sizeof(buf), "%d. UDP client", i+1);
		sendto(fd, buf, sizeof((buf)), 0, (struct sockaddr *)&ssi, sizeof(ssi));
		printf("Send(%s:%d)%s\n", inet_ntoa(ssi.sin_addr), ntohs(ssi.sin_port), buf);
	}

	close(fd);

	return EXIT_SUCCESS;
}
