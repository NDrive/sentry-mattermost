INSTALL="cd ~/plugins && python setup.py install"

bootstrap:
	docker-compose up -d
	docker-compose exec sentry bash -c $(INSTALL)
	docker-compose exec sentry_worker bash -c $(INSTALL)
	docker-compose exec sentry_cron bash -c $(INSTALL)
	docker-compose exec sentry sentry upgrade

restart:
	docker-compose restart sentry sentry_worker sentry_cron
