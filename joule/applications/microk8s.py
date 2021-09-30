import backoff
import json
import socket
import yaml

from subprocess import check_output, CalledProcessError

from joule.applications import BaseApplication, BaseProvider, Event, Events, logging


class Microk8sApplication(BaseApplication):
    """
    MicroK8s Application.
    """

    name: str = "microk8s"

    @staticmethod
    @backoff.on_exception(backoff.expo, CalledProcessError)
    def _label_node(instance_name: str) -> None:
        """
        Label the MicroK8s node with the matching cloud instance ID to make
        it easier to find later.

        Wrapped in a backoff as `wait ready` doesn't seem to be enough.

        :param instance_name: String
        :return: None
        """
        check_output(
            [
                "sudo",
                "microk8s",
                "kubectl",
                "label",
                "nodes",
                socket.gethostname(),
                "joule_instance={}".format(instance_name),
            ]
        )

    def _get_token_from_microk8s(self) -> str:
        """
        Run microk8s add-node to generate a token.

        :return: str
        """
        logging.debug("Generating token")
        return (
            check_output(["sudo", "microk8s", "add-node", "--token-ttl", "-1"])
            .decode()
            .split()[15]
        )

    def is_essential(self) -> bool:
        """
        Check whether this microk8s instance is a voter.

        :return: False
        """
        out: str = check_output(["microk8s", "status", "--format", "yaml"]).decode()
        parsed: dict = yaml.safe_load(out)

        if not parsed.get("high-availability"):
            return False

        my_ip: str = socket.gethostbyname(socket.gethostname())

        for node in parsed["high-availability"]["nodes"]:
            ip: str = node["address"].split(":")[0]
            role: str = node["role"]
            if ip == my_ip and role == "voter":
                return True

        return False

    def join(self, provider: BaseProvider, event: Event) -> None:
        """
        Run microk8s join with the token provided.

        Once the node has started, we need to tag it with the EC2 ID in
        order to find it again later.

        :param provider: BaseProvider instance of specific cloud
        :param event: Event object from queue
        :return: None
        """
        check_output(["sudo", "microk8s", "join", str(event.payload["token"])])
        check_output(["sudo", "microk8s", "status", "--wait-ready"])
        self._label_node(event.instance)

    def launch(self, provider: BaseProvider, event: Event) -> None:
        """
        Generate a token using microk8s add-node and then push it to
        the queue for consumption.

        :param provider: BaseProvider instance of specific cloud
        :param event: Event object from queue
        :return: None
        """
        token: str = self._get_token_from_microk8s()

        payload: dict = {"token": token}

        provider.send_join_to_message_queue(self, event, payload)

    def terminate(self, provider: BaseProvider, event: Event) -> None:
        """
        Retrieve the correct instance using the EC2 instance ID, then
        remove it from the microk8s cluster.

        :param provider: BaseProvider instance of specific cloud
        :param event: Event object from queue
        :return: None
        """
        out: str = check_output(
            [
                "sudo",
                "microk8s",
                "kubectl",
                "--output=json",
                "get",
                "nodes",
                "-l",
                "joule_instance={}".format(event.instance),
            ]
        ).decode()
        desc: dict = json.loads(out)
        hostname: str = desc["items"][0]["metadata"]["labels"]["kubernetes.io/hostname"]
        check_output(["sudo", "microk8s", "remove-node", hostname, "--force"])
