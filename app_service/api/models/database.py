from typing import List, Union, Optional
from pydantic import BaseModel

class Column(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None

class Table(BaseModel):
    schema: str
    name: str
    columns: List[Column]
    primary_keys: List[str]

class TableSchema(BaseModel):
    tables: List[Table]

class TableStat(BaseModel):
    schema: str
    table: str
    row_count: int

class DatabaseStats(BaseModel):
    database_size: str
    tables: List[TableStat]

class DatabaseStatsResponse(BaseModel):
    tables: List[TableStat]
    message: Optional[str] = None

class ColumnDetail(BaseModel):
    column_name: str
    data_type: str
    is_nullable: Optional[str] = None
    column_default: Optional[str] = None

class TableSchemaDetail(BaseModel):
    table_name: str
    columns: List[ColumnDetail]

class SchemaDetailsResponse(BaseModel):
    schema_details: List[TableSchemaDetail]
    message: Optional[str] = None 