# NAME: Stewart Dulaney,Pariya Samandi
# EMAIL: sdulaney@ucla.edu,pari.samandi@gmail.com
# ID: 904064791,205092357

CC = python3
ID = 904064791
LAB = 3b
ARCHIVE = lab$(LAB)-$(ID).tar.gz
sources = lab$(LAB).py Makefile README

build: lab$(LAB)

lab$(LAB):
	$(CC) lab$(LAB).py

dist: clean
	tar -czf $(ARCHIVE) $(sources)

clean:
	-rm $(ARCHIVE)
