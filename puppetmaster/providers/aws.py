import boto3
import json

from ec2_metadata import ec2_metadata
from typing import (
    Iterator,
    Optional
)

from puppetmaster.providers import (
    BaseProvider,
    Event,
    Events,
    logging
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
        logging.info('Using AWS Provider.')
        self.instance_id = ec2_metadata.instance_id

        if not region:
            region = ec2_metadata.region
            self._region = region

        sqs = boto3.resource('sqs', region_name=self._region)
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
                msg.delete()
                yield Event(event=Events.LAUNCH, instance=loaded.get('EC2InstanceId'))

            elif loaded.get('Event') == 'autoscaling:EC2_INSTANCE_TERMINATE':
                msg.delete()
                yield Event(event=Events.TERMINATE, instance=loaded.get('EC2InstanceId'))

            elif loaded.get('Event') == 'microk8s:join':
                if loaded.get('EC2InstanceId') == self.instance_id:
                    msg.delete()
                    yield Event(event=Events.JOIN, instance=loaded.get('EC2InstanceId'), token=loaded.get('Token'))

    def remove_node_from_microk8s(self, instance: str) -> None:
        """
        Replace the AWS internal instance ID with the real hostname.

        :return: None
        """
        ec2 = boto3.resource('ec2', region_name=self._region)
        instance = ec2 \
        .describe_instances(InstanceIds=[instance]) \
        .get('Reservations')[0] \
        .get('Instances')[0] \
        .get('PrivateDnsName') \
        .split('.')[0]

        super().remove_node_from_microk8s(instance)


    def send_token_to_message_queue(self, token: str, instance: str) -> None:
        """
        Add the generated token to the queue.
        """
        self.queue.send_message(MessageBody=json.dumps({
            'Event': 'microk8s:join',
            'EC2InstanceId': instance,
            'Token': token
        }))
