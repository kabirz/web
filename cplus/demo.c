#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	char *ip = "51.52.53.54";
	int a1 = inet_addr(ip);	 /* NBO (Big Endian) */

	struct in_addr inp;
	int a2 = inet_aton(ip, &inp); /* NBO (Big Endian) */

	int c = inet_network(ip); /* LBO (Litte Endian) */
	char *ip_str = inet_ntoa(inp);

	printf("inet_addr: %08x, , inet_aton: %08x, inet_network: %08x, inet_ntoa: %s\n", a1, inp.s_addr, c, ip_str);
	return EXIT_SUCCESS;
}

/* output
 * inet_addr: 36353433, , inet_aton: 36353433, inet_network: 33343536, inet_ntoa: 51.52.53.54
 */
