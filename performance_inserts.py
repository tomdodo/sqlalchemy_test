import json
import sys
from uuid import uuid4

from models.entry import Entry
from utils import record_queries, measure_time, get_session

ROWS_TO_INSERT = 10

description_factory = lambda prefix, index: f"{prefix}-row-{index}"


def _insert_with_add_multiple_commits(db, batch_id):
    inserted_ids = []
    for index in range(0, ROWS_TO_INSERT):
        entry = Entry(description=description_factory(batch_id, index))
        db.add(entry)
        db.commit()
        inserted_ids.append(entry.id)

    return inserted_ids


def _insert_with_add_single_commit(db, batch_id):
    entries = [
        Entry(description=description_factory(batch_id, index))
        for index in range(0, ROWS_TO_INSERT)
    ]
    for entry in entries:
        db.add(entry)

    db.commit()
    inserted_ids = [entry.id for entry in entries]
    return inserted_ids


def _insert_with_add_all(db, batch_id):
    entries = [
        Entry(description=description_factory(batch_id, index))
        for index in range(0, ROWS_TO_INSERT)
    ]
    db.add_all(entries)
    db.commit()

    inserted_ids = [entry.id for entry in entries]
    return inserted_ids


def _insert_with_bulk_save_objects(db, batch_id):
    last_id_before_insert = (
        db.query(Entry.id).order_by(Entry.id.desc()).limit(1).scalar()
    )
    # pass a list of instances of Entry model
    entries = [
        Entry(description=description_factory(batch_id, index))
        for index in range(0, ROWS_TO_INSERT)
    ]
    db.bulk_save_objects(entries)
    # you must fetch the IDs yourself
    inserted_ids = [
        id for id, in db.query(Entry.id).filter(Entry.id > last_id_before_insert).all()
    ]
    db.commit()
    return inserted_ids


def _insert_with_bulk_insert_mappings(db, batch_id):
    last_id_before_insert = (
        db.query(Entry.id).order_by(Entry.id.desc()).limit(1).scalar()
    )
    # pass a list of dictionaries where keys are the properties in the Entry model
    mappings = [
        {"description": description_factory(batch_id, index)}
        for index in range(0, ROWS_TO_INSERT)
    ]
    db.bulk_insert_mappings(Entry, mappings)
    # you must fetch the IDs yourself
    inserted_ids = [
        id for id, in db.query(Entry.id).filter(Entry.id > last_id_before_insert).all()
    ]
    db.commit()
    return inserted_ids


PARAM_TO_FUNCTION_MAP = {
    "add_multiple_commits": _insert_with_add_multiple_commits,
    "add_single_commit": _insert_with_add_single_commit,
    "add_all": _insert_with_add_all,
    "bulk_save_objects": _insert_with_bulk_save_objects,
    "bulk_insert_mappings": _insert_with_bulk_insert_mappings,
}


if __name__ == "__main__":
    param = sys.argv[1]
    fn = PARAM_TO_FUNCTION_MAP.get(param)
    if not fn:
        raise NotImplementedError(f"Invalid parameter: {param}")

    batch_id = uuid4().hex
    db = get_session()

    with record_queries() as queries:
        with measure_time() as measurement:
            inserted_ids = fn(db, batch_id)

    print(f"============== RESULTS ({param}) ===========")
    print(
        f"*** Inserted IDs ({len(inserted_ids)}): {inserted_ids[0]}...{inserted_ids[-1]}"
    )
    print(f"*** Emitted {len(queries)} queries:\n")
    print(json.dumps(queries, indent=2, default=str))
    print(f"*** total duration (s): {measurement.seconds}")
