## Diagnostic tool

### Usage

```python
python app.py
Fire trace:
1. Initial component
2. ('The function received no value for the required argument:', 'servers_file')

Type:        function
String form: <function run at 0x1090c6ea0>
File:        app.py
Line:        112
Docstring:   Diagnostic cli app

Arguments:
    servers_file {str} -- a plain text file with list of servers

Keyword Arguments:
    workers {int} -- number of threads (default: {5})

Usage:       app.py SERVERS_FILE [WORKERS]
             app.py --servers-file SERVERS_FILE [--workers WORKERS]
```

### Inlined (flat) dockerfile

```
docker build -f Dockerfile.cli -t cli .
docker run -v `pwd`:/app -it cli python app.py --servers-file=...
```

### Regular dockerfile

```
docker build -f Dockerfile -t cli .
docker run -v `pwd`:/app  -it cli python app.py --servers-file=...
```
