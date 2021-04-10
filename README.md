# Screenshots API

This repository contains the source code for my screenshots API.<br>
The API is very simple to use and configure on your own server.<br>

### Configuration

- Clone this repository on your own server
- Rename `config.sample.py` to `config.py`
- Modify the contents of `config.py` to suit your needs (especially `API_KEY`)
- Run `docker-compose up -d`
- Configure your reverse proxy

### Client Side

You can find the code for the client side script [here](https://github.com/Fumaz/Screenshots-Client).