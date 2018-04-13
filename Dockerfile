
FROM python:3.6

MAINTAINER Alex Myasoedov <msoedov@gmail.com>

WORKDIR /app

RUN pip install fire requests retry yaspin

COPY app.py .
CMD ["python", "app.py"]
