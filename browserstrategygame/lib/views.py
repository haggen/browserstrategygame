from sqlalchemy import MetaData, inspect, event, sql
from sqlalchemy.ext import compiler
from sqlalchemy.schema import DDLElement
from sqlalchemy.engine.base import Connection
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.selectable import Select


class CreateView(DDLElement):
    def __init__(self, name: str, selectable: sql.selectable.Select):
        self.name = name
        self.selectable = selectable


class DropView(DDLElement):
    def __init__(self, name: str):
        self.name = name


@compiler.compiles(CreateView)
def _create_view(element: CreateView, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (
        element.name,
        compiler.sql_compiler.process(element.selectable, literal_binds=True),
    )


@compiler.compiles(DropView)
def _drop_view(element: DropView, compiler, **kw):
    return "DROP VIEW %s" % (element.name)


def view_exists(ddl: Table, target: Table, connection: Connection, **kw):
    return ddl.name in inspect(connection).get_view_names()


def view_doesnt_exist(ddl: Table, target: Table, connection: Connection, **kw):
    return not view_exists(ddl, target, connection, **kw)


def view(name: str, metadata: MetaData, selectable: Select):
    table = sql.table(name)

    table._columns._populate_separate_keys(
        column._make_proxy(table) for column in selectable.selected_columns
    )

    event.listen(
        metadata,
        "after_create",
        CreateView(name, selectable).execute_if(callable_=view_doesnt_exist),
    )
    event.listen(
        metadata, "before_drop", DropView(name).execute_if(callable_=view_exists)
    )
    return table
