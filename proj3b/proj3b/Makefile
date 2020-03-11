# NAME: Stewart Dulaney,Pariya Samandi
# EMAIL: sdulaney@ucla.edu,pari.samandi@gmail.com
# ID: 904064791,205092357

CC = python3
ID = 904064791
LAB = 3b
ARCHIVE = lab$(LAB)-$(ID).tar.gz
sources = lab$(LAB).py lab$(LAB).sh Makefile README

build: lab$(LAB)

lab$(LAB):
	-ln lab$(LAB).sh lab$(LAB)
	-chmod +x lab$(LAB)

dist: clean
	-tar -czf $(ARCHIVE) $(sources)

clean:
	-rm $(ARCHIVE)
