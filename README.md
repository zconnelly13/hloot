# Hloot

### Prerequisites

- Docker Desktop https://www.docker.com/products/docker-desktop/t

### Setup

```bash
cp .env.dist .env
```

The default values should work here except for the midjourney api key. I
do most of my development with test images, though, which you can do by
by leaving the midjourney api key set to "DEV".

### Running the Game Locally

```bash
make build
make up
open localhost/
```

### Production

The backend is hosted on Heroku and the frontend is hosted on github pages.
It's automatically tested and deployed via github actions when changes are
made to the `main` branch.

- Frontend -> https://zconnelly13.github.io/hloot
- Backend -> https://hloot-9504ba8d8956.herokuapp.com/

It's a jackbox-style game where you run the host on a main screen and then
everyone plays from their phones.

### Running the Tests

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export $(cat .env | xargs)
make test
```

### Setting Up Dall-E Mini
```
pip install pyyaml==5.4.1 --ignore-installed
pip install -q dalle-mini
pip install -q git+https://github.com/patil-suraj/vqgan-jax.git

pip install ipywidgets
pip install --upgrade tqdm
```

### Running AUTOMATIC1111

see: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Installation-on-Apple-Silicon
