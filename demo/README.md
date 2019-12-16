# Album Graph Demo

This is a demo of Album Graph, and instructions on how to run it.


# Getting Start

* Start the gremlin service in [apache-tinkerpop-gremlin-server](apache-tinkerpop-gremlin-server)
```bash
cd apache-tinkerpop-gremlin-server
bash start.sh
```

* Add data to graph database [data](data)
```bash
cd data
python add_data_to_gremlin.py
python server.py
```

* Start the [frontend](frontend)
```bash
npm install
npm start
```
