"""Tiny REST API on top of the DigiClips MySQL container."""
import os
from datetime import date
from typing import Optional

import pymysql
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="DigiClips mini API", version="0.1")


def db():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.get("/health")
def health():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS caption_lines FROM text_line")
        return {"status": "ok", **cur.fetchone()}


@app.get("/outlets")
def list_outlets():
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT o.outlet_id, o.call_sign, o.network, o.media_class, m.name AS market"
            " FROM outlet o JOIN market m USING (market_id) ORDER BY o.call_sign"
        )
        return cur.fetchall()


@app.get("/outlets/{outlet_id}/chunks")
def outlet_chunks(outlet_id: int):
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM outlet WHERE outlet_id=%s", (outlet_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="outlet not found")
        cur.execute(
            "SELECT chunk_id, start_time, end_time FROM media_chunk WHERE outlet_id=%s ORDER BY start_time",
            (outlet_id,),
        )
        return cur.fetchall()


@app.get("/mentions")
def mentions(
    keyword: str = Query(..., min_length=2),
    call_sign: Optional[str] = None,
    day: Optional[date] = None,
    include_overlap: bool = False,
    limit: int = Query(25, ge=1, le=100),
):
    """Search caption text. Overlap lines are hidden by default so words are not duplicated."""
    sql = (
        "SELECT o.call_sign, t.spoken_at, t.frame_no, t.content"
        " FROM text_line t JOIN media_chunk c USING (chunk_id) JOIN outlet o USING (outlet_id)"
        " WHERE t.content LIKE %s"
    )
    args = [f"%{keyword}%"]
    if call_sign:
        sql += " AND o.call_sign = %s"
        args.append(call_sign.upper())
    if day:
        sql += " AND DATE(t.spoken_at) = %s"
        args.append(day)
    if not include_overlap:
        sql += " AND t.in_overlap = FALSE"
    sql += " ORDER BY t.spoken_at LIMIT %s"
    args.append(limit)
    with db() as conn, conn.cursor() as cur:
        cur.execute(sql, args)
        rows = cur.fetchall()
    return {"keyword": keyword, "count": len(rows), "results": rows}
