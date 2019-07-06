# -*- coding:utf-8 -*-


try:
    from pyramid.httpexceptions import HTTPForbidden
except ImportError:
    class HTTPForbidden(Exception):
        """Placeholder class for when pyramid is not available"""


class DomainError(Exception):
    """An error emitted from the domain code"""


class DomainForbiddenError(DomainError, HTTPForbidden):
    """Raised when an action is forbidden"""


class DomainAcquisitionAttributeError(DomainError, AttributeError):
    """Attribute not found"""


class DomainTraversalKeyError(DomainError, KeyError):
    """Raised when there is a key error from domain traversal"""


class DomainCollectionError(DomainError):
    """Raised when there is an error in the domain collection"""


class DomainCollectionNotListable(DomainCollectionError):
    """Raised when an atempt is made to list items in a collection which is unlistable"""


class DomainCollectionUnsupportedCriteria(DomainCollectionError):
    """Raised when a criteria is given to a collection which is not supported"""


class DomainRecordIdTypeError(DomainError, TypeError):
    """Raised when atempting to construct an ID type"""


class DomainRecordUpdateError(DomainError):
    """Raised when an update failure occured"""


class WorkflowTransitionError(DomainError):
    """Raised when the system is unble to perform a workflow transition"""


class WorkflowUnknownActionError(WorkflowTransitionError):
    """Raised when an attempt to transition to a workflow that doesn't exit"""


class WorkflowIllegalTransitionError(WorkflowTransitionError):
    """Raised when the workflow transition is correct but wasn't allowed from the current state"""
