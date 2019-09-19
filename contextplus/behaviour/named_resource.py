# -*- coding:utf-8 -*-
"""Add ability to create named travserable resources.


class Foo(DomainBase):

    @resource('my-resource')
    def my_resource(self):
        return Child(parent=self)

"""


class NamedResourceFactoryDecorator(object):
    def __init__(self, name, factory):
        """Initialize decorator"""
        self.name = name
        self.factory = factory

    def __get__(self, inst, owner):
        """Some serious depp python stuff going on here....

        The get magic method allows an object to behave as a class property such as @property.
        It returns the attribute of the owner instance or owner class depending on if the
        attribute that is accessed is on the instance or the class object. E.g. A.foo and A().foo
        both call the __get__ method for a propertyish object "foo". In our case we want
        self to be returned on the class object so the named resource is discoverable by
        iterating the class objects contents and testing isinstance, yet the instance of the
        class needs the function to be working too. So both these need to work::

            obj['foo']
            obj.get_foo()

        """

        if inst is None:
            # the attribute access is on the class object
            return self

        # return a wrapped factory method for an attribute on an instance object
        def method():

            try:
                resource_path_names = inst.path_names + (self.name,)
                cached_resource = inst.acquire.resource_cache_get(resource_path_names)
            except AttributeError:
                cached_resource = None
            if cached_resource is not None:
                return cached_resource

            # Create new resource object
            new_resource = self.factory(inst)

            # it is a bit presumptions to set the __parent__, so we don't and leave it for the factory

            # Set the name of the resource (if the factory hasn't done it)
            if getattr(new_resource, "__name__", None) is None:
                if hasattr(
                    new_resource, "set_name"
                ):  # lets not always assume that we have a pyramid object
                    new_resource.set_name(self.name)
                else:
                    new_resource.__name__ = self.name

            try:
                inst.acquire.resource_cache_save(new_resource)
            except AttributeError:
                pass
            return new_resource

        return method


def resource(name):
    def config_factory(factory):
        return NamedResourceFactoryDecorator(name=name, factory=factory)

    return config_factory


class NamedResourceBehaviour(object):
    """THe behaviour class which add the ability to traverse named resources"""

    def get_named_resource(self, name, default=None):
        """Return a named resource

        named resources are traversable by self[name], this function is called
        by __getitem__ to obtain the object for a given name. By default this
        function looks object factories which are marked on the class with the attribute
        tinterface_factory_for. get_tinterfaces doesn't iterate through the instance
        properties in order to prevent bringing into memory evey attribute.

        tinterface_factory_for can only be a string. For example:

            class A(DomainBase):

                def get_blahs_collection(self):
                    return Blahs()
                get_blah_collection.tinterface_factory_for = 'blahs'

        Then A()['blahs'] would be an instance of Blahs.

        Note that on successive calls a new object is returned to prevent any
        circular references occurring.

        Arguments:
            name: The name of the tinterface. This must be a string.
            default: The object to be returned if no interface was found.

        Returns:
            object: If the the tinterface is found
            None: If no tinterface is found
        """
        cls = type(self)
        for cls_name in dir(cls):
            cls_item = getattr(cls, cls_name, None)
            if isinstance(cls_item, NamedResourceFactoryDecorator):
                if cls_item.name == name:
                    return getattr(self, cls_name)()
        return default

    def iter_named_resources(self):
        """Iterate through tinterfaces"""
        cls = type(self)
        for cls_name in dir(cls):
            cls_item = getattr(cls, cls_name, None)
            if isinstance(cls_item, NamedResourceFactoryDecorator):
                yield getattr(self, cls_name)()

    def __getitem__(self, key):
        """Return an item contained in this contextplus object.

        Override to return a named resource if it exists
        """
        assert isinstance(key, str), "Only string keys are supported on __getitem__"
        item = self.get_named_resource(key)
        if item is not None:
            return item
        else:
            return super().__getitem__(key)
