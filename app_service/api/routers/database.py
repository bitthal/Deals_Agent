from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import asyncpg
from logger_config import logger

from ..dependencies.database import get_db_connection
from ..models.database import DatabaseStats, TableSchema

router = APIRouter(
    prefix="/database",
    tags=["database"],
    responses={404: {"description": "Not found"}},
)

@router.get("/stats", response_model=DatabaseStats)
async def get_database_stats(conn: asyncpg.Connection = Depends(get_db_connection)):
    """
    Get database statistics including table counts and row counts.
    """
    try:
        # Get table statistics
        table_stats = await conn.fetch("""
            SELECT 
                schemaname as schema,
                relname as table,
                n_live_tup as row_count
            FROM pg_stat_user_tables
            ORDER BY schemaname, relname;
        """)
        
        # Get database size
        db_size = await conn.fetchval("""
            SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        
        # Format results
        tables = []
        for stat in table_stats:
            tables.append({
                "schema": stat["schema"],
                "table": stat["table"],
                "row_count": stat["row_count"]
            })
        
        return {
            "database_size": db_size,
            "tables": tables
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get database statistics")

@router.get("/schema/{table_prefix}", response_model=TableSchema)
async def get_table_schema(
    table_prefix: str,
    conn: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Get schema information for tables matching the given prefix.
    """
    try:
        # Get column information
        columns = await conn.fetch("""
            SELECT 
                table_schema,
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name LIKE $1
            ORDER BY table_schema, table_name, ordinal_position;
        """, f"{table_prefix}%")
        
        # Get primary key information
        primary_keys = await conn.fetch("""
            SELECT
                tc.table_schema,
                tc.table_name,
                kc.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kc
                ON kc.table_name = tc.table_name
                AND kc.table_schema = tc.table_schema
                AND kc.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name LIKE $1;
        """, f"{table_prefix}%")
        
        # Format results
        tables = {}
        for col in columns:
            table_key = f"{col['table_schema']}.{col['table_name']}"
            if table_key not in tables:
                tables[table_key] = {
                    "schema": col["table_schema"],
                    "name": col["table_name"],
                    "columns": [],
                    "primary_keys": []
                }
            
            tables[table_key]["columns"].append({
                "name": col["column_name"],
                "type": col["data_type"],
                "nullable": col["is_nullable"] == "YES",
                "default": col["column_default"]
            })
        
        # Add primary keys
        for pk in primary_keys:
            table_key = f"{pk['table_schema']}.{pk['table_name']}"
            if table_key in tables:
                tables[table_key]["primary_keys"].append(pk["column_name"])
        
        return {
            "tables": list(tables.values())
        }
    except Exception as e:
        logger.error(f"Error getting table schema: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get table schema") 