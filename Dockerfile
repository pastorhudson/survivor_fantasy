FROM python:3.13-slim AS build

WORKDIR /app

COPY survivor.py pyproject.toml README.md ./
COPY survivor_files ./survivor_files

RUN python survivor.py --output index.html

FROM nginx:alpine

COPY --from=build /app/index.html /usr/share/nginx/html/index.html
COPY --from=build /app/survivor_files /usr/share/nginx/html/survivor_files
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
