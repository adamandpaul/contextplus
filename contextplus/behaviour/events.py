# -*- coding:utf-8 -*-
"""Add ability to for objects to emeit events or handle events


class Foo(DomainBase):

    @handle('save')
    def handle_save(self, event):
        pass

    def save(self):
        self.emeit("save", {"some obj"})

"""


class Event(object):
    def __init__(self, target, name, data):
        self.target = target
        self.name = name
        self.data = data


class HandlerDecorator(object):
    def __init__(self, handler, event_names=None, priority=None):
        """Initialize decorator"""
        self.handler = handler
        self.event_names = event_names
        self.priority = priority

    def match(self, event):
        if self.event_names is None:
            return True
        else:
            return event.name in self.event_names

    def __get__(self, inst, owner):
        """Some serious depp python stuff going on here....

        The get magic method allows an object to behave as a class property such as @property.
        It returns the attribute of the owner instance or owner class depending on if the
        attribute that is accessed is on the instance or the class object. E.g. A.foo and A().foo
        both call the __get__ method for a propertyish object "foo". In our case we want
        self to be returned on the class object so the named resource is discoverable by
        iterating the class objects contents and testing isinstance, yet the instance of the
        class needs the function to be working too. See also the named resource decorator.
        """

        if inst is None:
            # the attribute access is on the class object
            return self

        # return a wrapped handler method for an attribute on an instance object
        def method(*args, **kwargs):
            return self.handler(inst, *args, **kwargs)

        return method


def handle(*event_names, priority=None):
    def config_handler(handler):
        return HandlerDecorator(handler=handler, event_names=event_names, priority=priority)

    return config_handler


class EventsBehaviour(object):
    """THe behaviour class which add the ability to traverse named resources"""

    _event_handlers = None

    @property
    def event_handlers(self):
        """Returns a list of tuples of (EventDecorator instance, bound_handler) from this object
        and ancestor objects from self.acquire.event_handlers
        """
        if self._event_handlers is not None:
            return self._event_handlers

        # Get event handlers for self
        ordered = []
        unordered = []
        cls = type(self)
        for cls_name in dir(cls):
            cls_item = getattr(cls, cls_name, None)
            if isinstance(cls_item, HandlerDecorator):
                bound_handler = getattr(self, cls_name)
                if cls_item.priority is not None:
                    ordered.append((cls_item, bound_handler))
                else:
                    unordered.append((cls_item, bound_handler))
        ordered.sort(key=lambda h: h[0].priority)

        # get parent event handlers
        try:
            parent = self.parent.acquire.event_handlers
        except AttributeError:
            parent = []

        # Combine, cache and return
        handlers = [*ordered, *unordered, *parent]
        self._event_handlers = handlers
        return handlers

    def emit(self, name, data=None):
        """Emit an event to event handlers from the property self.event_handlers"""
        data = data or {}
        event = Event(self, name, data)
        for decorated, bound_handler in self.event_handlers:
            if decorated.match(event):
                bound_handler(event)
