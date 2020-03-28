.DEFAULT_GOAL := main
PWD := $(dir $(abspath $(firstword $(MAKEFILE_LIST))))

main:
	@docker build . -t johnpeter-discord
run:
	@docker run --env-file=.env -e GOOGLE_APPLICATION_CREDENTIALS=/local/serviceAccount.json -v $(PWD)/secrets:/local:ro johnpeter-discord
