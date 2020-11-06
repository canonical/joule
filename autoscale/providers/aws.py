import boto3
import json
import socket

from datetime import datetime
from ec2_metadata import ec2_metadata
from typing import Iterator, Optional

from autoscale.providers import BaseProvider, Event, Events, logging


class AwsProvider(BaseProvider):
    """
    AWS Provider.
    """

    def __init__(self, region: Optional[str] = None) -> None:
        """
        Setup AWS API objects.

        :param region: String overwrite region from metadata server
        :return: None
        """
        logging.info("Using AWS Provider.")
        self.instance_id: str = ec2_metadata.instance_id

        if not region:
            region: str = ec2_metadata.region
            self._region: str = region

        sqs: object = boto3.resource("sqs", region_name=self._region)
        self.queue: object = sqs.get_queue_by_name(QueueName="MicroK8s")

        self.asg: object = boto3.client("autoscaling", region_name=self._region)

    def mark_essential(self, *applications: object) -> None:
        """
        Mark instance as protected if required.

        :param: application: BaseApplication
        :return: None
        """
        if datetime.now().second != 0:
            return  # Run every minute.

        asg_name: str = self.asg.describe_auto_scaling_instances(
            InstanceIds=[ec2_metadata.instance_id], MaxRecords=1
        )["AutoScalingInstances"][0]["AutoScalingGroupName"]

        for app in applications:
            is_essential: bool = app.is_essential()
            self.asg.set_instance_protection(
                InstanceIds=[ec2_metadata.instance_id],
                AutoScalingGroupName=asg_name,
                ProtectedFromScaleIn=is_essential,
            )
            logging.debug("essential={}".format(is_essential))

    def get_events_from_message_queue(self) -> Iterator[Optional[Event]]:
        """
        Read the SQS queue for messages and try to parse them into an event object.

        :return: Event
        """
        rx: object = self.queue.receive_messages()

        for msg in rx:
            loaded: dict = json.loads(msg.body)

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

    def send_token_to_message_queue(self, event: Event, token: str) -> None:
        """
        Add the generated token to the queue.

        :param event: Event object from queue
        :param token: String add-node token
        :return: None
        """
        self.queue.send_message(
            MessageBody=json.dumps(
                {
                    "Event": "microk8s:join",
                    "EC2InstanceId": event.instance,
                    "Token": token,
                }
            )
        )
