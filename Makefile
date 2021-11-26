run:
	@cd docker; docker-compose up

run-build:
	@cd docker; docker-compose up --build

run-build-force-recreate:
	@cd docker; docker-compose up --build --force-recreate --renew-anon-volumes mariadb