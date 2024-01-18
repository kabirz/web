#include <stdlib.h>
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

	struct sockaddr_in csi = {0};
	socklen_t socke_len = sizeof(csi); /* can't get client infomation if sock_len is 0 */
	struct sockaddr_in ssi = {
		.sin_addr.s_addr = inet_addr("0.0.0.0"),
		.sin_port = htons(5678),
		.sin_family = AF_INET,
	};

	int ret = bind(fd, (struct sockaddr *)&ssi, sizeof(ssi));
	if (ret < 0) {
		perror("Bind:");
	}
	int i = 0;
	while (i < 10) {
		ret = recvfrom(fd, buf, sizeof(buf), 0, (struct sockaddr *)&csi, &socke_len);
		if (ret > 0) {
			printf("from(%d:%s:%d)%s\n", socke_len, inet_ntoa(csi.sin_addr), ntohs(csi.sin_port), buf);
			i++;
		}
	}

	close(fd);


	return EXIT_SUCCESS;
}
