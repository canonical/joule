import json
import socket

from subprocess import check_output

from autoscale.applications import BaseApplication, BaseProvider, Event, Events, logging


class MicroK8sApplication(BaseApplication):
    """
    MicroK8s Application.
    """

    def _get_token_from_microk8s(self) -> str:
        """
        Run microk8s add-node to generate a token.

        :return: str
        """
        return (
            check_output(["sudo", "microk8s", "add-node", "--token-ttl", "-1"])
            .decode()
            .split()[15]
        )

    def join(self, provider: BaseProvider, event: Event) -> None:
        logging.info("JOIN: {}".format(event))
        check_output(["sudo", "microk8s", "join", event.token])
        check_output(["sudo", "microk8s", "status", "--wait-ready"])
        check_output(
            [
                "sudo",
                "microk8s",
                "kubectl",
                "label",
                "nodes",
                socket.gethostname(),
                "ec2={}".format(event.instance),
            ]
        )

    def launch(self, provider: BaseProvider, event: Event) -> None:
        logging.info("LAUNCH: {}".format(event))
        token: str = self._get_token_from_microk8s()
        provider.send_token_to_message_queue(event, token)

    def terminate(self, provider: BaseProvider, event: Event) -> None:
        logging.info("TERMINATE: {}".format(event))
        out: str = check_output(
            [
                "sudo",
                "microk8s",
                "kubectl",
                "--output=json",
                "get",
                "nodes",
                "-l",
                "ec2={}".format(event.instance),
            ]
        )
        desc: dict = json.loads(out)
        hostname = (
            desc.get("items")[0]
            .get("metadata")
            .get("labels")
            .get("kubernetes.io/hostname")
        )
        check_output(["sudo", "microk8s", "remove-node", hostname, "--force"])
