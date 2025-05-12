
all:
	for dir in $(shell cat projects.txt); do \
		make -C $$dir; \
	done

clean:
	for dir in $(shell cat projects.txt); do \
		make -C $$dir clean; \
	done

.PHONY: all
