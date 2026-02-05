import re
import socket
import logging
from functools import cache
from typing import Callable

from localstack.utils.docker_utils import DOCKER_CLIENT
from localstack.extensions.api import Extension
from localstack.utils.container_utils.container_client import PortMappings
from localstack.utils.net import get_addressable_container_host
from localstack.utils.sync import retry

LOG = logging.getLogger(__name__)


class DatabaseDockerContainerExtension(Extension):
    name: str
    image_name: str
    container_ports: list[int]
    command: list[str] | None
    volumes: list[str] | None

    def __init__(
        self,
        image_name: str,
        container_ports: list[int],
        command: list[str] | None = None,
        env_vars: dict[str, str] | None = None,
        volumes: list[str] | None = None,
        health_check_port: int | None = None,
        health_check_fn: Callable[[], bool] | None = None,
    ):
        self.image_name = image_name
        if not container_ports:
            raise ValueError("container_ports is required")
        self.container_ports = container_ports
        self.container_name = re.sub(r"\W", "-", f"ls-ext-{self.name}")
        self.command = command
        self.env_vars = env_vars
        self.volumes = volumes
        self.health_check_port = health_check_port or container_ports[0]
        self.health_check_fn = health_check_fn
        self.container_host = get_addressable_container_host()

    def on_extension_load(self):
        LOG.info("Loading %s extension", self.name)

    def on_platform_start(self):
        LOG.info("Starting %s extension - launching container", self.name)
        self.start_container()

    def on_platform_shutdown(self):
        self._remove_container()

    @cache
    def start_container(self) -> None:
        LOG.debug("Starting extension container %s", self.container_name)

        port_mapping = PortMappings()
        for port in self.container_ports:
            port_mapping.add(port)

        kwargs = {}
        if self.command:
            kwargs["command"] = self.command
        if self.env_vars:
            kwargs["env_vars"] = self.env_vars
        if self.volumes:
            kwargs["volumes"] = self.volumes

        DOCKER_CLIENT.run_container(
            self.image_name,
            detach=True,
            remove=True,
            name=self.container_name,
            ports=port_mapping,
            **kwargs,
        )

        def _check_health():
            if self.health_check_fn:
                assert self.health_check_fn()
            else:
                self._check_tcp_port(self.container_host, self.health_check_port)

        try:
            retry(_check_health, retries=60, sleep=1)
        except Exception as e:
            LOG.info("Failed to connect to container %s: %s", self.container_name, e)
            self._remove_container()
            raise

        LOG.info(
            "Successfully started extension container %s on %s:%s",
            self.container_name,
            self.container_host,
            self.health_check_port,
        )

    def _check_tcp_port(self, host: str, port: int, timeout: float = 2.0) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            sock.close()
        except (socket.timeout, socket.error) as e:
            raise AssertionError(f"Port {port} not ready: {e}")

    def _remove_container(self):
        LOG.debug("Stopping extension container %s", self.container_name)
        DOCKER_CLIENT.remove_container(
            self.container_name, force=True, check_existence=False
        )

    def get_connection_info(self) -> dict:
        return {}
