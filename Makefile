.PHONY : all
all:
	poetry export -f requirements.txt > requirements.txt
	snapcraft

.PHONY : clean
clean:
	rm -f requirements.txt
	rm -f microk8s-puppetmaster*.snap