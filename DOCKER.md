# Dockerizing the MathJax Proxy

## Combined Container: Slobby + MathJax Proxy

This container runs **both** the Slobby server (port 8013) and the MathJax proxy (port 8014) in a single container.

## Building the Image

```bash
docker build -t mathjax-proxy .
```

## Running the Container

The container runs both Slobby and the MathJax proxy together.

### Option 1: Using Make (recommended)

```bash
# Build if needed, then run
make

# Or just run (requires image to already exist)
make run
```

### Option 2: Manual docker run

```bash
docker run -d --name mathjax-proxy \
  -p 127.0.0.1:8013:8013 \
  -p 127.0.0.1:8014:8014 \
  -v /opt/aard.wikipedia:/opt/aard \
  -e SLOBBY_FILE=/opt/aard/enwiki.slob \
  mathjax-proxy
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SLOBBY_FILE` | `/opt/aard/enwiki.slob` | Path to the Slobby database file |
| `TARGET_HOST` | `127.0.0.1` | Hostname for internal communication (Slobby→proxy) |
| `TARGET_PORT` | `8013` | Slobby server port (internal) |

## Accessing the Services

Once running, access the services at:
- **Slobby**: `http://127.0.0.1:8013`
- **MathJax Proxy**: `http://127.0.0.1:8014`
- **Lookup page**: `http://127.0.0.1:8014/lookup`

## Stopping the Container

```bash
# If running with docker run
docker stop <container_id>

# If using docker-compose
docker-compose down
```
