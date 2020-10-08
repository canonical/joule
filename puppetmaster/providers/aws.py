import boto3
import json
import socket

from ec2_metadata import ec2_metadata
from typing import Iterator, Optional

from puppetmaster.providers import BaseProvider, Event, Events, check_output, logging


class AwsProvider(BaseProvider):
    """
    AWS Provider.
    """

    def __init__(self, region: Optional[str] = None):
        """
        Setup AWS API objects.

        :param region: Overwrite region from metadata server
        :return: None
        """
        logging.info("Using AWS Provider.")
        self.instance_id = ec2_metadata.instance_id

        if not region:
            region = ec2_metadata.region
            self._region = region

        sqs = boto3.resource("sqs", region_name=self._region)
        self.queue = sqs.get_queue_by_name(QueueName="MicroK8s-Cluster")

    def get_events_from_message_queue(self) -> Iterator[Optional[Event]]:
        """
        Read the SQS queue for messages and try to parse them into an event object.

        :return: Event
        """
        rx = self.queue.receive_messages()

        for msg in rx:
            loaded = json.loads(msg.body)

            if loaded.get("Event") == "autoscaling:EC2_INSTANCE_LAUNCH":
                msg.delete()
                yield Event(event=Events.LAUNCH, instance=loaded.get("EC2InstanceId"))

            elif loaded.get("Event") == "autoscaling:EC2_INSTANCE_TERMINATE":
                msg.delete()
                yield Event(
                    event=Events.TERMINATE, instance=loaded.get("EC2InstanceId")
                )

            elif loaded.get("Event") == "microk8s:join":
                if loaded.get("EC2InstanceId") == self.instance_id:
                    msg.delete()
                    yield Event(
                        event=Events.JOIN,
                        instance=loaded.get("EC2InstanceId"),
                        token=loaded.get("Token"),
                    )

    def remove_node_from_microk8s(self, event: Event) -> None:
        """
        Replace the AWS internal instance ID with the real hostname.

        :return: None
        """
        out = check_output(["sudo", "microk8s", "kubectl", "--output=json", "get", "nodes", "-l", "ec2={}".format(event.instance)])
        desc = json.loads(out)
        event.instance = desc.get("items")[0].get("metadata").get("labels").get("kubernetes.io/hostname")

        super().remove_node_from_microk8s(event)

    def send_token_to_message_queue(self, event: Event) -> None:
        """
        Add the generated token to the queue.
        """
        self.queue.send_message(
            MessageBody=json.dumps(
                {
                    "Event": "microk8s:join",
                    "EC2InstanceId": event.instance,
                    "Token": event.token,
                }
            )
        )

    def join_node_to_microk8s(self, event: Event) -> None:
        """
        Run microk8s join to add instance to cluster.
        """
        dns = socket.gethostname()
        check_output(
            [
                "sudo",
                "microk8s",
                "kubectl",
                "nodes",
                dns,
                "ec2={}".format(event.instance),
            ]
        )

        super().join_node_to_microk8s(event.token)
