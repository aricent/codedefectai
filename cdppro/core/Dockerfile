FROM ubuntu:18.04
RUN apt-get update -y 
RUN apt-get install -y apt-utils
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-dev 
RUN apt-get install -y python3-mysqldb
RUN apt-get install -y python3-pymysql
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y cron
RUN apt-get install -y git

# Make ssh dir
RUN mkdir /root/.ssh/

# Create known_hosts
RUN touch /root/.ssh/known_hosts
# Add bitbuckets key
RUN ssh-keyscan -H github.com >> /root/.ssh/known_hosts

#ADD crontab /etc/cron.d/crontab
#RUN chmod 0600 /etc/cron.d/crontab
#RUN crontab -u root /etc/cron.d/crontab
#RUN touch /var/log/cron.log

RUN mkdir /cdpscheduler

COPY ./requirements.txt /cdpscheduler/requirements.txt
COPY . /cdpscheduler
WORKDIR /cdpscheduler
RUN pip3 install -r requirements.txt

STOPSIGNAL SIGINT

COPY cronfile /etc/cron.d/cronfile
RUN chmod 0644 /etc/cron.d/cronfile
RUN crontab /etc/cron.d/cronfile
RUN touch /var/log/cron.log
CMD ["cron", "-f"]

