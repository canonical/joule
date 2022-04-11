# AWS MicroK8s Cloud Formation Template

Deploy this via the AWS web console and adjust the created Auto Scale Group.

![Topology diagram](topoligy-diagram.png?raw=true "Topology Diagram")

## Components

### SQS and SNS

The SQS and SNS are used to communicate between the Auto Scale Group and Joule.

### Launch Template

The launch template specifies the type of EC2 instances to be created, as well as their AMI. Note that the AMI may have to be changed across regions.

#### User Data

The `UserData` section of the launch template is what installs and configures MicroK8s and Joule.

### Auto Scaling Group

The Auto Scale Group defines the boundaries of scaling. Set `MinSize`, `MaxSize` and `DesiredCapacity` to your requirements.

### Lambda

In order to ensure that the initial cluster does not shard, we need to elect a first node to start the cluster. This is done by tagging any initial node with `joule:enrolled` = `1`. This Lambda handles that initial tagging and is triggered once the Auto Scaling Group is created.

## Notes

### Key Pair

Change the key pair with any you wish to use to be able to SSH into the started nodes.
