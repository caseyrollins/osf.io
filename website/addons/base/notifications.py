# -*- coding: utf-8 -*-

from furl import furl
from datetime import datetime

from website.notifications.emails import notify, remove_users_from_subscription
from website.notifications.utils import move_file_subscription
from website.notifications.model import BaseEvent
from website.models import Node


def get_notify_type(user, node, event, payload):
    """Given an event it returns a new instance of the file event classes"""
    event_options = {
        'file_added': UpdateFileEvent,
        'file_updated': UpdateFileEvent,
        'file_removed': SimpleFileEvent,
        'folder_created': SimpleFileEvent,
        'addon_file_moved': MoveFileEvent,
        'addon_file_copied': MoveFileEvent
    }
    return event_options[event](user, node, event, payload)


class FileEvent(BaseEvent):
    """File event base class"""

    def __init__(self, user, node, event, payload):
        super(FileEvent, self).__init__(user, node, event)
        self.payload = payload
        self.event_sub = None
        self.message = "Blank message"
        self.url = None
        self.guid = None

    @classmethod
    def unserialize(cls, user, node, event, payload):
        """Selects the correct subclass"""
        return get_notify_type(user, node, event, payload)

    def perform(self):
        """Calls emails.notify"""
        notify(
            uid=self.node_id,
            event=self.event_sub,
            user=self.user,
            node=self.node,
            timestamp=self.timestamp,
            message=self.message,
            gravatar_url=self.gravatar_url,
            url=self.url
        )

    def form_message(self):
        f_type, action = tuple(self.event.split("_"))
        name = self.payload['metadata']['materialized'].strip('/')
        self.message = '{} {} "<b>{}</b>".'.format(action, f_type, name)

    def form_event(self):
        self.event_sub = "file_updated"

    def form_url(self):
        f_url = furl(self.node.absolute_url)
        return f_url

    def form_guid(self):
        addon = self.node.get_addon(self.payload['provider'])
        path = self.payload['metadata']['path']
        path = path if path.startswith('/') else '/' + path
        self.guid, created = addon.find_or_create_file_guid(path)


class UpdateFileEvent(FileEvent):
    """
    Class for simple file operations such as updating, adding files
    """
    def __init__(self, user, node, event, payload):
        super(UpdateFileEvent, self).__init__(user, node, event, payload)
        self.form_guid()
        self.form_event()
        self.form_message()
        self.form_url()

    def form_event(self):
        self.event_sub = self.guid.guid_url.strip('/') + '_file_updated'

    def form_url(self):
        f_url = super(UpdateFileEvent, self).form_url()
        f_url.path = self.guid.guid_url
        self.url = f_url.url


class SimpleFileEvent(FileEvent):
    """
    Class for file/folder operations that don't lead to a specific place
    """
    def __init__(self, user, node, event, payload):
        super(SimpleFileEvent, self).__init__(user, node, event, payload)
        self.form_event()
        self.form_message()
        self.form_url()

    def form_url(self):
        """Forms a url that points at the file view"""
        f_url = super(SimpleFileEvent, self).form_url()
        f_url.path = self.node.web_url_for('collect_file_trees')
        self.url = f_url.url


class MoveFileEvent(FileEvent):
    """
    Class for move and copy files. Users could be removed from subscription.
    """
    def __init__(self, user, node, event, payload):
        super(MoveFileEvent, self).__init__(user, node, event, payload)
        self.source_guid = None
        self.source_node = Node.load(self.payload['source']['node']['_id'])
        self.form_guid()
        self.source_event_sub = None
        self.form_event()
        self.source_url = None
        self.form_url()
        self.form_message()

    def perform(self):
        if 'moved' in self.event:
            rm_users = move_file_subscription(self.source_event_sub, self.source_node,
                                              self.event_sub, self.node)
            message = self.message + ' You have been removed due to insufficient permissions.',
            remove_users_from_subscription(rm_users, self.source_event_sub, self.user, self.source_node,
                                           timestamp=self.timestamp, gravatar_url=self.gravatar_url,
                                           message=message, url=self.source_url)
        else:
            self.message += ' You are not subscribed to the new file, follow link to add subscription.'
        super(MoveFileEvent, self).perform()

    def form_message(self):
        addon, f_type, action = tuple(self.event.split("_"))
        destination_name = self.payload['destination']['materialized'].strip('/')
        source_name = self.payload['source']['materialized'].strip('/')
        self.message = '{} "<b>{}</b>" from {} in {} to "<b>{}</b>" in {} in {}'.format(
            f_type, source_name, self.payload['source']['addon'], self.payload['source']['node']['title'],
            destination_name, self.payload['destination']['addon'], self.payload['destination']['node']['title']
        )

    def form_event(self):
        self.event_sub = self.guid.guid_url.strip('/') + '_file_updated'
        self.source_event_sub = self.source_guid.guid_url.strip('/') + '_file_updated'

    def form_url(self):
        f_url = super(MoveFileEvent, self).form_url()
        f_url.path = self.guid.guid_url
        self.url = f_url.url
        # source url
        if 'copied' in self.event:
            f_url.path = self.source_guid.guid_url
        else:
            f_url.path = self.node.web_url_for('collect_file_trees')
        self.source_url = f_url.url

    def form_guid(self):
        """Produces both guids"""
        addon = self.node.get_addon(self.payload['destination']['provider'])
        path = self.payload['destination']['path']
        path = path if path.startswith('/') else '/' + path
        self.guid, created = addon.find_or_create_file_guid(path)
        addon = self.source_node.get_addon(self.payload['source']['provider'])
        path = self.payload['source']['path']
        path = path if path.startswith('/') else '/' + path
        self.source_guid, created = addon.find_or_create_file_guid(path)
