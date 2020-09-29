import boto3
import json

from ec2_metadata import ec2_metadata
from typing import (
    Iterator,
    Optional
)

from . import (
    BaseProvider,
    Event,
    Events
)


class AwsProvider(BaseProvider):
    """
    AWS Provider.
    """
    def __init__(self,
        region: Optional[str] = None):
        """
        Setup AWS API objects.

        :param region: Overwrite region from metadata server
        :return: None
        """
        if not region:
            region = ec2_metadata.region

        sqs = boto3.resource('sqs', region_name=region)
        self.queue = sqs.get_queue_by_name(QueueName='MicroK8s-Cluster')

    def get_events_from_message_queue(self) -> Iterator[Optional[Event]]:
        """
        Read the SQS que for messages and try to parse them into an event object.

        :return: Event
        """
        rx = self.queue.receive_messages()

        for msg in rx:
            loaded = json.loads(msg.body)

            if loaded.get('Event') == 'autoscaling:EC2_INSTANCE_LAUNCH':
                yield Event(event=Events.LAUNCH, instance=loaded.get('EC2InstanceId'))

            elif loaded.get('Event') == 'autoscaling:EC2_INSTANCE_TERMINATE':
                yield Event(event=Events.TERMINATE, instance=loaded.get('EC2InstanceId'))
