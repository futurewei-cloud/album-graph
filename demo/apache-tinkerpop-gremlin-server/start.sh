#!/bin/sh

url="https://archive.apache.org/dist/tinkerpop/3.4.1/apache-tinkerpop-gremlin-server-3.4.1-bin.zip"
local_file="apache-tinkerpop-gremlin-server-3.4.1-bin.zip"
local_dir="apache-tinkerpop-gremlin-server-3.4.1"
 
wget -c $url -O $local_file
unzip $local_file
cd $local_dir
bin/gremlin-server.sh conf/gremlin-server-modern.yaml 
