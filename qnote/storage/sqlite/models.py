import re
import peewee as pw
from playhouse.sqlite_ext import SqliteExtDatabase


__all__ = [
    'Note', 'Notebook', 'Tag', 'NoteToNotebook', 'NoteToTag',
    'get_database', 'proxy',
]


proxy = pw.Proxy()

def get_database(storage_path):
    db = SqliteExtDatabase(
        storage_path,
        pragmas=(
            ('cache_size', -1024 * 16), # 16MB page-cache
            ('journal_mode', 'wal'),
            ('foreign_keys', 1),
        ),
        regexp_function=True,
    )
    return db


def make_table_name(cls_model):
    model_name = pascal_to_snake_case(cls_model.__name__)
    return '%s%s' % (model_name, '_tbl')


def pascal_to_snake_case(name):
    regex = re.compile('(?<!^)(?=[A-Z])')
    return regex.sub(r'_', name).lower()


class BaseModel(pw.Model):
    class Meta:
        database = proxy
        legacy_table_names = False
        table_function = make_table_name


class Tag(BaseModel):
    id = pw.AutoField()
    name = pw.CharField(unique=True)


class Note(BaseModel):
    id = pw.AutoField()
    uuid = pw.UUIDField()
    title = pw.CharField(max_length=256)
    create_time = pw.TimestampField()
    update_time = pw.TimestampField()
    content = pw.TextField()


class NoteToTag(BaseModel):
    note = pw.ForeignKeyField(Note)
    tag = pw.ForeignKeyField(Tag)

    class Meta:
        primary_key = pw.CompositeKey('note', 'tag')


class Notebook(BaseModel):
    id = pw.AutoField()
    name = pw.CharField(unique=True)
    create_time = pw.TimestampField()
    update_time = pw.TimestampField()


class NoteToNotebook(BaseModel):
    note = pw.ForeignKeyField(Note)
    notebook = pw.ForeignKeyField(Notebook)

    class Meta:
        primary_key = pw.CompositeKey('note', 'notebook')
