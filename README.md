Qdrant on LocalStack
[![Install LocalStack Extension](https://cdn.localstack.cloud/gh/extension-badge.svg)](https://app.localstack.cloud/extensions/remote?url=git+https://github.com/qdrant/localstack-qdrant/#egg=qdrant-extension)
====================

This repo contains a [LocalStack Extension](https://github.com/localstack/localstack-extensions) for developing [Qdrant](https://qdrant.tech)-based applications locally.

Qdrant is a high-performance vector search engine and database for the next generation of AI applications.

After installing the extension, a Qdrant server instance will become available and can be accessed using the [REST](https://qdrant.tech/documentation/interfaces/#api-reference) and [gRPC](https://qdrant.tech/documentation/interfaces/#grpc-interface) APIs.

## Connection Details

Once the extension is running, you can connect to Qdrant using the retrieved connection info.

- Host: `localhost` (or the Docker host if running in a container)
- HTTP Port: `6333` (mapped from the container)
- GRPC Port: `6334` (mapped from the container)

If you have configured `LOCALSTACK_QDRANT_API_KEY`, you must provide it to the client.
If you have configured TLS (`LOCALSTACK_QDRANT_TLS_CERT` and `LOCALSTACK_QDRANT_TLS_KEY`), you must use HTTPS.

## Configuration

The following environment variables can be passed to the LocalStack container to configure the extension:

- `LOCALSTACK_QDRANT_TAG`: Version of Qdrant to use (optional, default: `latest`)
- `LOCALSTACK_QDRANT_API_KEY`: API Key to secure Qdrant instance (optional)
- `LOCALSTACK_QDRANT_TLS_CERT`: Path to TLS certificate file (optional, enables HTTPS)
- `LOCALSTACK_QDRANT_TLS_KEY`: Path to TLS key file (optional, enables HTTPS)
- Any environment variable starting with `LOCALSTACK_QDRANT__` will be passed to the Qdrant container, allowing you to configure Qdrant as per the [documentation](https://qdrant.tech/documentation/guides/configuration/).
  - Example: `LOCALSTACK_QDRANT__SERVICE__MAX_REQUEST_SIZE_MB=64`

## Prerequisites

- Docker
- LocalStack Pro (free trial available)
- `localstack` CLI
- `make`

## Install from GitHub repository

This extension can be installed directly from this Github repo via:

```bash
localstack extensions install "git+https://github.com/qdrant/localstack-qdrant/#egg=qdrant-extension"
```

## License

The code in this repo is available under the Apache 2.0 license.