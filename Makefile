.PHONY: bootstrap-python, bootstrap-docker, restart, bootstrap, restart, deploy

INSTALL="cd plugins && python setup.py install"

bootstrap-docker:
	docker-compose up -d
	docker exec -it --user root sentrymattermost_celery-worker_1 bash -c $(INSTALL)
	docker exec -it --user root sentrymattermost_celery-beat_1 bash -c $(INSTALL)
	docker exec -it --user root sentrymattermost_sentry_1 bash -c $(INSTALL)
	docker exec -it sentrymattermost_sentry_1 sentry upgrade

restart:
	docker-compose restart sentry celery-worker celery-beat

bootstrap: bootstrap-docker restart

clean:
	rm -rf .env build dist *.egg-info

deploy:
	python setup.py register
	python setup.py sdist upload
