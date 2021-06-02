import boto3
import json
import logging

from datetime import datetime
from ec2_metadata import ec2_metadata
from typing import Iterator, Optional

from mypy_boto3_autoscaling.client import AutoScalingClient
from mypy_boto3_sqs.service_resource import Message, Queue

from joule.providers import BaseProvider, Event, Events, logging


class AwsProvider(BaseProvider):
    """
    AWS Provider.
    """

    def __init__(self, *applications: object) -> None:
        """
        Setup AWS API objects.

        :param: applications: BaseApplication
        :return: None
        """

        super().__init__(*applications)

        self.instance_id: str = ec2_metadata.instance_id

        self._region: str = ec2_metadata.region

        queue_url: str = boto3.client("sqs", region_name=self._region).list_queues()[
            "QueueUrls"
        ][
            0
        ]  # Get first queue found.
        self.queue: Queue = boto3.resource("sqs", region_name=self._region).Queue(
            queue_url
        )

        self.asg: AutoScalingClient = boto3.client(
            "autoscaling", region_name=self._region
        )

    def mark_essential(self) -> None:
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

        for app in self.applications:
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
        rx: list[Message] = self.queue.receive_messages()

        for msg in rx:
            try:
                loaded: dict[str, str] = json.loads(json.loads(msg.body).get("Message"))
            except TypeError:
                loaded: dict[str, str] = json.loads(msg.body)

            if loaded.get("Event") == "autoscaling:EC2_INSTANCE_LAUNCH":
                msg.delete()
                yield Event(event=Events.LAUNCH, instance=loaded["EC2InstanceId"])

            if loaded.get("Event") == "autoscaling:EC2_INSTANCE_TERMINATE":
                msg.delete()
                yield Event(event=Events.TERMINATE, instance=loaded["EC2InstanceId"])

            for app in self.applications:
                if loaded.get("Event") == "{}:join".format(app.name):
                    if loaded.get("EC2InstanceId") == self.instance_id:
                        msg.delete()
                        yield Event(
                            event=Events.JOIN,
                            instance=loaded["EC2InstanceId"],
                            payload=json.loads(loaded["Payload"]),
                            application=app,
                        )

            logging.info("Ignoring event: {}".format(loaded))

    def send_join_to_message_queue(
        self, application: object, event: Event, payload: dict
    ) -> None:
        """
        Add the generated token to the queue.

        :param application: BaseApplication
        :param event: Event object from queue
        :param payload: Dictionary
        :return: None
        """
        self.queue.send_message(
            MessageBody=json.dumps(
                {
                    "Event": "{}:join".format(application.name),
                    "EC2InstanceId": event.instance,
                    "Payload": json.dumps(payload),
                }
            )
        )
