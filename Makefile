# Makefile para unDAAD

CC     = gcc
CFLAGS = -std=c99 -march=native -O3 -fomit-frame-pointer

undaad: undaad.c condactos.h
	$(CC) $(CFLAGS) -o $@ undaad.c

clean:
	rm -f undaad

distclean:
	rm -f undaad *~
