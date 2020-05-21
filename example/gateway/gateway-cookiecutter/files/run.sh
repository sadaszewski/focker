#!/bin/sh

mkdir -p /cookiecutter/output/meta && \
cp -v /cookiecutter/input/meta/cookiecutter.json \
  /cookiecutter/output/meta/cookiecutter.json && \
\
cp -v /cookiecutter/input/nginx-http/nginx.conf \
  /cookiecutter/templates/nginx-http/\{\{cookiecutter.directory_name\}\}/nginx.conf && \
cp -v /cookiecutter/input/meta/cookiecutter.json \
  /cookiecutter/templates/nginx-http/cookiecutter.json && \
\
cp -v /cookiecutter/input/nginx-https/nginx.conf \
  /cookiecutter/templates/nginx-https/\{\{cookiecutter.directory_name\}\}/nginx.conf && \
cp -v /cookiecutter/input/meta/cookiecutter.json \
  /cookiecutter/templates/nginx-https/cookiecutter.json && \
\
cd /cookiecutter/output && \
cookiecutter --no-input /cookiecutter/templates/nginx-http directory_name=nginx-http && \
\
cd /cookiecutter/output && \
cookiecutter --no-input /cookiecutter/templates/nginx-https directory_name=nginx-https
