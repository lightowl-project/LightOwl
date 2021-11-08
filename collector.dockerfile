FROM telegraf:1.12.3
RUN apt update && apt install -y netcat
CMD ["telegraf", "-config", "/etc/telegraf/telegraf.conf", "-config-directory", "/etc/telegraf/telegraf.d"]