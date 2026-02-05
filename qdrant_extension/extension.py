import os
import logging

from qdrant_extension.utils.docker import DatabaseDockerContainerExtension

LOG = logging.getLogger(__name__)


DEFAULT_QDRANT_PORT = 6333
DEFAULT_QDRANT_GRPC_PORT = 6334


class QdrantExtension(DatabaseDockerContainerExtension):
    name = "qdrant-extension"
    DOCKER_IMAGE = "qdrant/qdrant:{}"

    def __init__(self):
        qdrant_port = DEFAULT_QDRANT_PORT
        qdrant_grpc_port = DEFAULT_QDRANT_GRPC_PORT
        self.api_key = os.environ.get("LOCALSTACK_QDRANT_API_KEY")
        self.qdrant_version = os.environ.get("LOCALSTACK_QDRANT_TAG") or "latest"

        env_vars = {}
        if self.api_key:
            env_vars["QDRANT__SERVICE__API_KEY"] = self.api_key

        for key, value in os.environ.items():
            if key.startswith("LOCALSTACK_QDRANT__"):
                env_vars[key.replace("LOCALSTACK_", "", 1)] = value

        tls_cert_path = os.environ.get("LOCALSTACK_QDRANT_TLS_CERT")
        tls_key_path = os.environ.get("LOCALSTACK_QDRANT_TLS_KEY")
        volumes = []

        if tls_cert_path and tls_key_path:
            volumes.append(f"{tls_cert_path}:/qdrant/tls/cert.pem")
            volumes.append(f"{tls_key_path}:/qdrant/tls/key.pem")

            env_vars["QDRANT__TLS__HTTPS__ENABLE"] = "true"
            env_vars["QDRANT__TLS__HTTPS__CERT"] = "/qdrant/tls/cert.pem"
            env_vars["QDRANT__TLS__HTTPS__KEY"] = "/qdrant/tls/key.pem"
            self.use_https = True
        else:
            self.use_https = False

        super().__init__(
            image_name=self.DOCKER_IMAGE.format(self.qdrant_version),
            container_ports=[qdrant_port, qdrant_grpc_port],
            env_vars=env_vars,
            volumes=volumes if volumes else None,
        )

        self.qdrant_port = qdrant_port
        self.qdrant_grpc_port = qdrant_grpc_port

    def get_connection_info(self) -> dict:
        protocol = "https" if self.use_https else "http"
        return {
            "host": self.container_host,
            "port": self.qdrant_port,
            "grpc_port": self.qdrant_grpc_port,
            "protocol": protocol,
            "url": f"{protocol}://{self.container_host}:{self.qdrant_port}",
            "grpc_url": f"{protocol}://{self.container_host}:{self.qdrant_grpc_port}",
        }
