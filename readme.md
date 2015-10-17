#Tornado Calculator API

This is a json web API designed for the challenge described
[here](https://github.com/juanpabloaj/calculator-api-challenge).

To run the server in a docker container you can execute:

    $ docker build .
    $ docker run -p 8888:8888 <your-image-id>

To test the api with `curl`:

    curl --data-urlencode "query={\"op\": \"+\", \"ops\": [1, 2]}" http://localhost:8888
