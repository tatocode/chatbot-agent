from __future__ import annotations

import aiomysql
from aiomysql import DictCursor
from fastmcp import FastMCP

mcp = FastMCP("MySQL")

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "charset": "utf8mb4",
    "autocommit": True,
    "cursorclass": DictCursor,
}

_pool: aiomysql.Pool | None = None


async def get_pool() -> aiomysql.Pool:
    global _pool

    if _pool is None:
        _pool = await aiomysql.create_pool(
            minsize=1,
            maxsize=20,
            **MYSQL_CONFIG,
        )

    return _pool


def _validate_identifier(name: str):
    if not name.replace("_", "").isalnum():
        raise ValueError(f"Invalid identifier: {name}")


# ===========================================================
# Database
# ===========================================================

@mcp.tool()
async def list_databases() -> list[dict]:
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SHOW DATABASES")
            return await cur.fetchall()


@mcp.tool()
async def list_tables(database: str) -> list[dict]:
    _validate_identifier(database)

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SHOW TABLES FROM `{database}`")
            return await cur.fetchall()


# ===========================================================
# Schema
# ===========================================================

@mcp.tool()
async def describe_table(
    database: str,
    table: str,
) -> list[dict]:
    _validate_identifier(database)
    _validate_identifier(table)

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"DESCRIBE `{database}`.`{table}`"
            )
            return await cur.fetchall()


@mcp.tool()
async def show_create_table(
    database: str,
    table: str,
) -> dict:
    _validate_identifier(database)
    _validate_identifier(table)

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SHOW CREATE TABLE `{database}`.`{table}`"
            )
            return await cur.fetchone()


@mcp.tool()
async def list_foreign_keys(
    database: str,
) -> list[dict]:
    _validate_identifier(database)

    sql = """
    SELECT
        TABLE_NAME,
        COLUMN_NAME,
        REFERENCED_TABLE_NAME,
        REFERENCED_COLUMN_NAME,
        CONSTRAINT_NAME
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA=%s
      AND REFERENCED_TABLE_NAME IS NOT NULL
    """

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, (database,))
            return await cur.fetchall()


# ===========================================================
# Preview
# ===========================================================

@mcp.tool()
async def preview_table(
    database: str,
    table: str,
    limit: int = 10,
) -> list[dict]:
    _validate_identifier(database)
    _validate_identifier(table)

    limit = max(1, min(limit, 100))

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"SELECT * FROM `{database}`.`{table}` LIMIT {limit}"
            )
            return await cur.fetchall()


# ===========================================================
# Query
# ===========================================================

READ_ONLY_PREFIX = (
    "select",
    "show",
    "describe",
    "desc",
    "with",
    "explain",
)


@mcp.tool()
async def execute_query(
    database: str,
    sql: str,
) -> list[dict]:
    _validate_identifier(database)

    sql = sql.strip()

    if not sql.lower().startswith(READ_ONLY_PREFIX):
        raise ValueError(
            "Only read-only SQL statements are allowed."
        )

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"USE `{database}`")
            await cur.execute(sql)

            if cur.description:
                return await cur.fetchall()

            return []


@mcp.tool()
async def explain_query(
    database: str,
    sql: str,
) -> list[dict]:
    _validate_identifier(database)

    sql = sql.strip()

    if not sql.lower().startswith(("select", "with")):
        raise ValueError(
            "Only SELECT statements can be explained."
        )

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"USE `{database}`")
            await cur.execute(f"EXPLAIN {sql}")
            return await cur.fetchall()


@mcp.tool()
async def get_database_schema(
    database: str,
) -> dict:

    _validate_identifier(database)

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:

            await cur.execute(
                """
                SELECT
                    TABLE_NAME,
                    COLUMN_NAME,
                    COLUMN_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COLUMN_KEY,
                    EXTRA,
                    COLUMN_COMMENT
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA=%s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                (database,),
            )

            columns = await cur.fetchall()

            await cur.execute(
                """
                SELECT
                    TABLE_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME,
                    CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA=%s
                  AND REFERENCED_TABLE_NAME IS NOT NULL
                """,
                (database,),
            )

            foreign_keys = await cur.fetchall()

    schema = {
        "database": database,
        "tables": {},
    }

    for col in columns:

        table = col["TABLE_NAME"]

        if table not in schema["tables"]:
            schema["tables"][table] = {
                "columns": [],
                "primary_keys": [],
                "foreign_keys": [],
            }

        schema["tables"][table]["columns"].append(
            {
                "name": col["COLUMN_NAME"],
                "type": col["COLUMN_TYPE"],
                "nullable": col["IS_NULLABLE"] == "YES",
                "default": col["COLUMN_DEFAULT"],
                "key": col["COLUMN_KEY"],
                "extra": col["EXTRA"],
                "comment": col["COLUMN_COMMENT"],
            }
        )

        if col["COLUMN_KEY"] == "PRI":
            schema["tables"][table]["primary_keys"].append(
                col["COLUMN_NAME"]
            )

    for fk in foreign_keys:
        schema["tables"][fk["TABLE_NAME"]]["foreign_keys"].append(
            {
                "column": fk["COLUMN_NAME"],
                "referenced_table": fk["REFERENCED_TABLE_NAME"],
                "referenced_column": fk["REFERENCED_COLUMN_NAME"],
                "constraint": fk["CONSTRAINT_NAME"],
            }
        )

    return schema


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )