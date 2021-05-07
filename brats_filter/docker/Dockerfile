FROM python:3.7

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           vim \
           cron \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir /app
WORKDIR /app

# Create the log file to be able to run tail
RUN touch /var/log/cron.log
#setup crontab
ADD crontab-script /etc/cron.d/task-cron
RUN chmod 0644 /etc/cron.d/task-cron

# this is the custom entry point
CMD /app/start.sh
