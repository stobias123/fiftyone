"""
Documents that track datasets and their sample schemas in the database.

| Copyright 2017-2021, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
import mongoengine as moe

import eta.core.utils as etau

from .document import Document, EmbeddedDocument
from .evaluation import EvaluationDocument
from .fields import DictField, LabelTargetsField, TargetsField


class SampleFieldDocument(EmbeddedDocument):
    """Description of a sample field."""

    name = moe.StringField()
    ftype = moe.StringField()
    subfield = moe.StringField(null=True)
    embedded_doc_type = moe.StringField(null=True)
    targets_name = moe.StringField(null=True)

    @classmethod
    def from_field(cls, field):
        """Creates a :class:`SampleFieldDocument` for a field.

        Args:
            field: a :class:``fiftyone.core.fields.Field`` instance

        Returns:
            a :class:`SampleFieldDocument`
        """
        return cls(
            name=field.name,
            ftype=etau.get_class_name(field),
            subfield=cls._get_attr_repr(field, "field"),
            embedded_doc_type=cls._get_attr_repr(field, "document_type"),
        )

    @classmethod
    def list_from_field_schema(cls, d):
        """Creates a list of :class:`SampleFieldDocument` objects from a field
        schema.

        Args:
             d: a dict generated by
                :func:`fiftyone.core.dataset.Dataset.get_field_schema`

        Returns:
             a list of :class:`SampleFieldDocument` objects
        """
        return [
            cls.from_field(field) for field in d.values() if field.name != "id"
        ]

    def matches_field(self, field):
        """Determines whether this sample field matches the given field.

        Args:
            field: a :class:``fiftyone.core.fields.Field`` instance

        Returns:
            True/False
        """
        if self.name != field.name:
            return False

        if self.ftype != etau.get_class_name(field):
            return False

        if self.subfield and self.subfield != etau.get_class_name(field.field):
            return False

        if (
            self.embedded_doc_type
            and self.embedded_doc_type
            != etau.get_class_name(field.document_type)
        ):
            return False

        return True

    @staticmethod
    def _get_attr_repr(field, attr_name):
        attr = getattr(field, attr_name, None)
        return etau.get_class_name(attr) if attr else None


class DatasetDocument(Document):
    """Backing document for datasets."""

    meta = {"collection": "datasets"}

    media_type = moe.StringField()
    name = moe.StringField(unique=True, required=True)
    sample_collection_name = moe.StringField(unique=True, required=True)
    persistent = moe.BooleanField(default=False)
    info = DictField(default=dict)
    evaluations = moe.DictField(
        moe.EmbeddedDocumentField(document_type=EvaluationDocument),
        default=dict,
    )
    sample_fields = moe.EmbeddedDocumentListField(
        document_type=SampleFieldDocument
    )
    default_targets = TargetsField(null=True)
    label_targets = LabelTargetsField(default=dict)
    frame_fields = moe.EmbeddedDocumentListField(
        document_type=SampleFieldDocument
    )
    version = moe.StringField(required=True, null=True)
