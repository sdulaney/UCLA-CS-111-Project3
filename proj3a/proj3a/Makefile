# NAME: Stewart Dulaney,Pariya Samandi
# EMAIL: sdulaney@ucla.edu,pari.samandi@gmail.com
# ID: 904-064-791,205-092-357

CC = gcc
CFLAGS = -g -Wall -Wextra -lm
ID = 904-064-791
LAB = 3a
ARCHIVE = lab$(LAB)-$(ID).tar.gz
sources = lab3a.c ext2_fs.h Makefile README

build: lab3a

lab3a:
	$(CC) $(CFLAGS) lab3a.c -o lab3a

dist: clean
	tar -czf $(ARCHIVE) $(sources)

clean:
	-rm lab3a
	-rm lab$(LAB)-904-064-791.tar.gz

