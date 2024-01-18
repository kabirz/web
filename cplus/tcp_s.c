#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

struct my_data {
	int fd;
	struct in_addr addr;
	in_port_t port;
};

void* start_send(void *buf)
{
	struct my_data *_mydata = buf;
	char data[64] = {0};

	int ret = recv(_mydata->fd, data, sizeof(data), 0);
	if (ret > 0) {
			printf("recive client(%s: %d): %s\n", inet_ntoa(_mydata->addr), ntohs(_mydata->port), data);
	};

	close(_mydata->fd);

	return NULL;
}

int main(int argc, char *argv[])
{
	int ret;
	struct my_data _my_data[3];
	pthread_t thread[3];
	int new_fd;
	char buf[64] = "Hello, This is TCP server";

	int fd = socket(AF_INET, SOCK_STREAM, 0);
	if (fd < 0) return -1;

	struct sockaddr_in client_si = {0};
	socklen_t sock_len = sizeof(client_si); /* can't get client infomation if sock_len is 0 */
	struct sockaddr_in local_si = {
		.sin_addr.s_addr = inet_addr("0.0.0.0"),
		.sin_port = htons(1234),
		.sin_family = AF_INET,
	};

	ret = bind(fd, (struct sockaddr *)&local_si, sizeof(local_si));
	if (ret < 0) {
		perror("Bind:");
	}

	if (listen(fd, 3) != 0) goto end_main;

	for(int i = 0; i < 3; i++) {
		new_fd = accept(fd, (struct sockaddr *)&client_si, &sock_len);
		printf("accept clinet(%s, %d), fd: %d\n", inet_ntoa(client_si.sin_addr), sock_len, new_fd);
		_my_data[i].fd = new_fd;
		_my_data[i].addr.s_addr = client_si.sin_addr.s_addr;
		_my_data[i].port = client_si.sin_port;
		ret = send(new_fd, buf, strlen(buf), 0);
		if (ret == -1)
			perror("Send:");
		pthread_create(&thread[i], NULL, start_send, _my_data+i);
	}
	pthread_join(thread[0], NULL);
	pthread_join(thread[1], NULL);
	pthread_join(thread[2], NULL);

end_main:
	close(fd);

	return EXIT_SUCCESS;
}
