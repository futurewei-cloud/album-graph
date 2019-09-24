# Album graph 

## Service API

| argument | description |	
|--------|--------|
|need | the type of the input data: img,tag,model,datetime,gpsrange, recommendation,allmodels|
|arg| input data|
|dataset| 'l' for large dataset(missing data for now), 's' for small dataset|


### Querying information of single image

base url: http://10.145.83.34:7000/albumgraph

There are six kinds of information you can query here: tag, datetime, gps, model, relationships, allimginfo

| argument | value |	
|--------|--------|
|need | 'img'|
|arg| image_id|
|dataset| 's'|
|output| 'tag','datetime','gps','model','relationships','allimginfo'|

- tag URI format sample: http://10.145.83.34:7000/albumgraph?need=img&output=tag&arg=45&dataset=s
- datetime URI format sample: http://10.145.83.34:7000/albumgraph?need=img&output=datetime&arg=45&dataset=s
- gps URI format sample: http://10.145.83.34:7000/albumgraph?need=img&output=gps&arg=45&dataset=s
- model URI format sample: http://10.145.83.34:7000/albumgraph?need=img&output=model&arg=45&dataset=s
- relationships URI format sample: http://10.145.83.34:7000/albumgraph?need=img&output=relationships&arg=45&dataset=s
- allimginfo URI format sample: http://10.145.83.34:7000/albumgraph?need=img&output=allimginfo&arg=45&dataset=s


### Building albums with the specific information

base url: http://10.145.83.34:7000/albumgraph

There are five kinds of album you can build here: tag, model, city, state, country

For example, if you want to build a album related to tag'Tree' or city'Bellevue' , you can use the following APIs: 

| argument | value |	
|--------|--------|
|need | 'tag', 'model', 'city', 'state', 'country'|
|arg| tag_id,model_id,Bellevue,Washington,United States of America|
|dataset| 's'|

- tag album URI format sample: http://10.145.83.34:7000/albumgraph?need=tag&arg=Tree&dataset=s
- model album URI format sample: http://10.145.83.34:7000/albumgraph?need=model&arg=iPhone 5s&dataset=s
- city album URI format sample: http://10.145.83.34:7000/albumgraph?need=city&arg=Bellevue&dataset=s
- state album URI format sample: http://10.145.83.34:7000/albumgraph?need=state&arg=Washington&dataset=s
- country album URI format sample: http://10.145.83.34:7000/albumgraph?need=country&arg=United States of America&dataset=s


Build your album with a date range:

| argument | value |	
|--------|--------|
|need | 'date'|
|start | YYYY/MM/DD HH:MM:SS|
|end | YYYY/MM/DD HH:MM:SS|
|dataset| 's'|

- date album URI format sample: http://localhost:7000/albumgraph?need=date&start=2016-04-09&end=2016-04-10&dataset=s
- You can also use this url with time http://localhost:7000/albumgraph?need=date&start=2016-04-09&end=2016-04-10 20:48:59&dataset=s

Build your album with a gps range:

| argument | value |	
|--------|--------|
|need | 'gps'|
|lat_lb | double|
|lat_ub | double|
|lon_lb | double|
|lon_ub | double|
|dataset| 's'|

- gps album URI format sample: http://10.145.83.34:7000/albumgraph?need=gpsrange&lat_lb=46&lat_ub=47&lon_lb=-123&lon_ub=-120&dataset=s

Build your album with graph recommendation algorithm from GES(If you input some tag, the system will return the most related images)

- recommendation album URI format sample: http://10.145.83.34:7000/albumgraph?need=recommondation&arg=Tree&dataset=s


Build your album with the face feature(We cluster the images with K-means, the images with similar face features have the same cluster_id)

- cluster album URI format sample: http://10.145.83.34:7000/albumgraph?need=cluster&arg=cluster_id&dataset=s

Build your album with some semantic words(For example, you can input subject'Pants', predicate'on', objects'Person', the system will return images including this relationship)

- semantic album URI format sample: http://10.145.83.34:7000/albumgraph?need=semantic&subj=Pants&predicate=on&obj=Person&dataset=s


### Querying information of all images

base url: http://10.145.83.34:7000/albumgraph

There are 2 kinds of information you can query here: allmodels, alltags, allrelationships

| argument | value |	
|--------|--------|
|need | 'allmodels','alltags','allrelationships'|
|arg| 'NA'|
|dataset| 's'|

- alltags URI format sample: http://10.145.83.34:7000/albumgraph?need=alltags&arg=NA&dataset=s
- allmodels URI format sample: http://10.145.83.34:7000/albumgraph?need=allmodels&arg=NA&dataset=s
- allrelationships URI format sample: http://10.145.83.34:7000/albumgraph?need=allrelationships&arg=NA&dataset=s
### Getting images

base url: http://10.145.83.34:7000/albumgraph

There are 3 kinds of image you can get here: original image, 800 * 600 image, 80*60 image

original image base url: http://10.145.83.34:7000/oimage

800 * 600 image base url: http://10.145.83.34:7000/mimage

80 * 60 image base url: http://10.145.83.34:7000/simage

| argument | value |	
|--------|--------|
|prefix | path_prefix|
|filename| 'XXX.jpg','XXX.png'...|

- original image URI format sample: http://10.145.83.34:7000/oimages?prefix=/nfs_3/data/album_graph_data/Lin/processed_images/&filename=G0010356.JPG
- 800 * 600 image URI format sample: http://10.145.83.34:7000/mimages?prefix=/nfs_3/data/album_graph_data/Lin/processed_images/&filename=G0010356.JPG
- 80 * 60 image URI format sample: http://10.145.83.34:7000/simages?prefix=/nfs_3/data/album_graph_data/Lin/processed_images/&filename=G0010356.JPG
