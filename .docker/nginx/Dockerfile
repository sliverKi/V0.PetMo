FROM nginx:latest
USER root
RUN apt-get update && apt-get install -y procps

RUN rm /etc/nginx/conf.d/default.conf
# COPY ./nginx.conf /etc/nginx/conf.d/
COPY ./conf.d/default.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /code/app/static/
