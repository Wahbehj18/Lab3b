#Jacob Wahbeh Valentin Lagunes
#Wahbehj18@g.ucla.edu valetinlagunes51@gmail.com
#105114897 505117243
#Makefile Lab3b

build:
	cp lab3b.py lab3b
	chmod +x lab3b

dist:
	tar -czf lab3b-505117243.tar.gz lab3b.py README Makefile

clean:
	rm -f lab3b lab3b-505117243.tar.gz

