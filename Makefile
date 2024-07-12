BUILDFILE:=python build.py

all:
	make buildrun
	
build:
	$(BUILDFILE) build

run:
	$(BUILDFILE) run

buildrun:
	make build
	make run

reset:
	$(BUILDFILE) reset

clean:
	$(BUILDFILE) clean

configurepath:
	$(BUILDFILE) configure path

configurebuild:
	$(BUILDFILE) configure build

configureall:
	make configurepath
	make configurebuild