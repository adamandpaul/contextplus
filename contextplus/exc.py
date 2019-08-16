# -*- coding:utf-8 -*-


class ContextPlusError(Exception):
    """An error emitted from the domain code"""


class AcquisitionAttributeError(ContextPlusError, AttributeError):
    """Attribute not found"""


class TraversalKeyError(ContextPlusError, KeyError):
    """Raised when there is a key error from domain traversal"""


class CollectionError(ContextPlusError):
    """Raised when there is an error in the domain collection"""


class CollectionNotListable(CollectionError):
    """Raised when an attempt is made to list items in a collection
    which cannot be listed"""


class CollectionUnsupportedCriteria(CollectionError):
    """Raised when a criteria is given to a collection which is not
    supported"""


class RecordError(ContextPlusError):
    """Raised in the context of a record"""


class RecordIdTypeError(RecordError, TypeError):
    """Raised when attempting to construct an ID type"""


class RecordUpdateError(RecordError):
    """Raised when an update failure occurred"""


class WorkflowTransitionError(ContextPlusError):
    """Raised when the system is unble to perform a workflow transition"""


class WorkflowUnknownActionError(WorkflowTransitionError):
    """Raised when an attempt to transition to a workflow that doesn't exit"""


class WorkflowIllegalTransitionError(WorkflowTransitionError):
    """Raised when the workflow transition is correct but wasn't allowed
    from the current state"""
