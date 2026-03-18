.PHONY: test brief serve demo-assets docker-build docker-run deploy-staging

test:
	PYTHONPATH=app/src python3 -m unittest discover -s app/src/tests -v

brief:
	PYTHONPATH=app/src python3 -m project_velocity

serve:
	PYTHONPATH=app/src python3 -m project_velocity serve --port 8000

demo-assets:
	PYTHONPATH=app/src python3 -m project_velocity demo-assets --output-dir /tmp/project-velocity-demo

docker-build:
	docker build -t project-velocity:local .

docker-run: docker-build
	docker run --rm -p 8000:8000 project-velocity:local

deploy-staging:
	bash ./.github/scripts/deploy-staging.sh
