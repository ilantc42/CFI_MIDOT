FROM ubuntu:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y make cron && \
    apt-get clean

# Copy the necessary files
COPY . /app
WORKDIR /app

# Run make setup
RUN make setup

# Add crontab file in the cron directory
RUN echo "0 0 1 */x * /app/script.bat" > /etc/cron.d/mycron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/mycron

# Apply cron job
RUN crontab /etc/cron.d/mycron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
