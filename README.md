# Joule

Named after [Joule expansion](https://en.wikipedia.org/wiki/Joule_expansion),
Joule helps you to automate the scaling of applications inside cloud scale
groups.

## How it works

Joule is split into 2 parts; the provider and the application. The provider's
main loop consumes an application in order to operate it.

### Provider

A provider object defines how Joule communicates with the cloud provider. It
listens to a scale group's event queue in order to prepare the application for
scale in and scale out events.

### Application

An application object defines how Joule drives the application you're running
at scale by responding to events from the provider.

### Events

There are 3 events that are abstracted from the provider into the application.

#### JOIN

Created after a new instance has started and is only handled on the new
instance. Use this for any configuration that needs to be done to the
application to join the cluster. For example, passing a token to the
application in order to authenticate it into the
cluster.

#### LAUNCH

Created on an existing instance when a new instance has been launched by the provider. Use
this for handling any actions required before the new instance are
joined to the cluster. It could be run on any existing instance in
the cluster. For example, adding the new instance to a list of
allowed hosts.

#### TERMINATE

Called on a remaining instance when an instance is terminated. Use this to cleanup anything
within the cluster after termination of an instance. It
could be run on any remaining instance on the cluster. For example,
removing the instance from a list of allowed hosts.
