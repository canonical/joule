import boto3
import json

from datetime import datetime
from ec2_metadata import ec2_metadata
from typing import Iterator, Optional, List, Dict, Any

from mypy_boto3_autoscaling.client import AutoScalingClient
from mypy_boto3_ec2 import EC2Client
from mypy_boto3_ec2.type_defs import DescribeTagsResultTypeDef
from mypy_boto3_sqs.service_resource import Message, Queue
from mypy_boto3_sqs.type_defs import ListQueuesResultTypeDef

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

        self._instance_id: str = ec2_metadata.instance_id

        self._region: str = ec2_metadata.region

        queues: ListQueuesResultTypeDef = boto3.client(
            "sqs", region_name=self._region
        ).list_queues()
        queue_url: str = queues["QueueUrls"][0]  # Get first queue found.

        self._queue: Queue = boto3.resource("sqs", region_name=self._region).Queue(
            queue_url
        )

        self._ec2: EC2Client = boto3.client("ec2", region_name=self._region)
        self._asg: AutoScalingClient = boto3.client(
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

        asg_name: str = self._asg.describe_auto_scaling_instances(
            InstanceIds=[ec2_metadata.instance_id], MaxRecords=1
        )["AutoScalingInstances"][0]["AutoScalingGroupName"]

        for app in self.applications:
            is_essential: bool = app.is_essential()
            self._asg.set_instance_protection(
                InstanceIds=[ec2_metadata.instance_id],
                AutoScalingGroupName=asg_name,
                ProtectedFromScaleIn=is_essential,
            )
            logging.debug("essential={}".format(is_essential))

    def mark_enrolled(self) -> None:
        """
        Mark this instance as being enrolled in the application's cluster.

        :return: None
        """
        self._ec2.create_tags(
            Resources=[self._instance_id],
            Tags=[
                {"Key": self._tag_enrolled["Key"], "Value": self._tag_enrolled["Value"]}
            ],
        )

    def is_enrolled(self) -> bool:
        """
        Return whether or not this instance has been enrolled into the
        application's cluster.

        :return: Boolean
        """
        result: DescribeTagsResultTypeDef = self._ec2.describe_tags(
            Filters=[
                {"Name": "resource-id", "Values": [self._instance_id]},
                {
                    "Name": "key",
                    "Values": [self._tag_enrolled["Key"]],
                },
            ],
        )

        if result.get("Tags", None):
            return True
        return False  # When none or empty list (no matches for tag key).

    def get_events_from_message_queue(self) -> Iterator[Optional[Event]]:
        """
        Read the SQS queue for messages and try to parse them into an event object.

        :return: Event
        """
        rx: List[Message] = self._queue.receive_messages(
            VisibilityTimeout=0, WaitTimeSeconds=1, MaxNumberOfMessages=10
        )

        for msg in rx:
            loaded: Dict[str, str] = {}
            try:
                loaded = json.loads(json.loads(msg.body).get("Message"))
            except TypeError:
                loaded = json.loads(msg.body)

            event: Optional[str] = loaded.get("Event")

            if self.is_enrolled():
                for app in self.applications:
                    if event == "{}:join".format(app.name):
                        if loaded.get("EC2InstanceId") == self._instance_id:
                            msg.delete()  # Clean up any duplicated events.

                if event == "autoscaling:TEST_NOTIFICATION":
                    msg.delete()  # AWS spam.

                if event == "autoscaling:EC2_INSTANCE_LAUNCH":
                    msg.delete()
                    yield Event(event=Events.LAUNCH, instance=loaded["EC2InstanceId"])

                if event == "autoscaling:EC2_INSTANCE_TERMINATE":
                    msg.delete()
                    yield Event(
                        event=Events.TERMINATE, instance=loaded["EC2InstanceId"]
                    )
            else:
                for app in self.applications:
                    if event == "{}:join".format(app.name):
                        if loaded.get("EC2InstanceId") == self._instance_id:
                            msg.delete()
                            yield Event(
                                event=Events.JOIN,
                                instance=loaded["EC2InstanceId"],
                                payload=json.loads(loaded["Payload"]),
                                application=app,
                            )

    def send_join_to_message_queue(
        self, application: Any, event: Event, payload: dict
    ) -> None:
        """
        Add the generated token to the queue.

        :param application: BaseApplication
        :param event: Event object from queue
        :param payload: Dictionary
        :return: None
        """
        self._queue.send_message(
            MessageBody=json.dumps(
                {
                    "Event": "{}:join".format(application.name),
                    "EC2InstanceId": event.instance,
                    "Payload": json.dumps(payload),
                }
            )
        )
