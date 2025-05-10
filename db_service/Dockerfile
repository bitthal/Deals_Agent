FROM postgres:15

# Copy initialization scripts
COPY ./init/ /docker-entrypoint-initdb.d/

# Set environment variables
ENV POSTGRES_DB=deals_db
ENV POSTGRES_USER=deals_user
ENV POSTGRES_PASSWORD=deals_password

# Expose PostgreSQL port
EXPOSE 5432 