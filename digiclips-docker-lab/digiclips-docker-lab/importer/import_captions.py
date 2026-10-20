"""Load sample closed-caption lines into MySQL.

Chunks overlap: the start (lead) of one chunk repeats the end (tail) of the
chunk before it. If a line falls in a time that an EARLIER chunk of the same
outlet already covers, it is flagged in_overlap so the API can skip it and not
show the same words twice.
"""
import csv
import os
from datetime import datetime, timedelta

import pymysql

CHUNK_MIN = 10


def connect():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        autocommit=False,
    )


def main():
    conn = connect()
    cur = conn.cursor()
    added = skipped = 0
    with open("sample/captions.csv", newline="") as f:
        for row in csv.DictReader(f):
            cur.execute("SELECT outlet_id FROM outlet WHERE call_sign=%s", (row["call_sign"],))
            found = cur.fetchone()
            if not found:
                print("unknown outlet, skipping:", row["call_sign"])
                skipped += 1
                continue
            start = datetime.fromisoformat(row["chunk_start"])
            end = start + timedelta(minutes=CHUNK_MIN)
            cur.execute(
                "INSERT IGNORE INTO media_chunk (outlet_id, start_time, end_time) VALUES (%s,%s,%s)",
                (found[0], start, end),
            )
            cur.execute(
                "SELECT chunk_id FROM media_chunk WHERE outlet_id=%s AND start_time=%s",
                (found[0], start),
            )
            chunk_id = cur.fetchone()[0]
            spoken = datetime.fromisoformat(row["spoken_at"])
            cur.execute(
                "SELECT 1 FROM media_chunk WHERE outlet_id=%s AND start_time<%s AND end_time>%s",
                (found[0], start, spoken),
            )
            in_overlap = cur.fetchone() is not None
            # do not insert the same line twice if the importer runs again
            cur.execute(
                "SELECT 1 FROM text_line WHERE chunk_id=%s AND frame_no=%s AND track_type='closed_caption'",
                (chunk_id, int(row["frame_no"])),
            )
            if cur.fetchone():
                skipped += 1
                continue
            cur.execute(
                "INSERT INTO text_line (chunk_id, track_type, frame_no, spoken_at, content, in_overlap)"
                " VALUES (%s,'closed_caption',%s,%s,%s,%s)",
                (chunk_id, int(row["frame_no"]), spoken, row["content"], in_overlap),
            )
            added += 1
    conn.commit()
    print(f"import done: {added} lines added, {skipped} skipped")


if __name__ == "__main__":
    main()
