from subprocess import check_output

from puppetmaster.applications import BaseApplication, BaseProvider, Event, Events


class MicroK8sApplication(BaseApplication):
    """
    MicroK8s Application.
    """

    def __init__(self):
        raise NotImplementedError("Must use a real application.")

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
        check_output(["sudo", "microk8s", "join", event.token])

    def launch(self, provider: BaseProvider, event: Event) -> None:
        token: str = self._get_token_from_microk8s()
        provider.send_token_to_message_queue(event, token)

    def terminate(self, provider: BaseProvider, event: Event) -> None:
        check_output(["sudo", "microk8s", "remove-node", event.instance, "--force"])
