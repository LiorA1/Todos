FROM python:3.10
ENV PYTHONUNBUFFERED=1
WORKDIR /todos
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD ["uvicorn" ,"main:app" ,"--host" ,"0.0.0.0" ,"--reload"]