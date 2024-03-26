#!/usr/bin/env python
# coding: utf-8
import glob
import json
import sys


def get_metadata(fn):
    start = "----------------------------"
    end = "-----------------------"
    with open(fn) as fh:
        metadata = {}
        is_metadata = False
        for line in fh:
            if line.strip() == start or line.strip() == end:
                pass
            elif line.strip() == "Metadata section of document":
                is_metadata = True
            elif line.strip() == "End of metadata section":
                return metadata
            elif is_metadata:
                key_value = line.strip().split(":")
                if len(key_value) == 2:
                    key, value = key_value
                    metadata[key] = value
                elif len(key_value) == 1:
                    metadata[key_value[0]] = None
                else:
                    pass


def get_reports_E(fn):
    end_1 = "-----------------------"
    end_2 = "End of metadata section"
    _start = False
    skip = True
    with open(fn) as fh:
        report = []
        for line in fh:
            if line.strip() == end_2:
                _start = True
            if line.strip() == end_1 and _start:
                skip = False
                continue
            if skip:
                continue
            if line.strip() == "":
                if report:
                    yield report
                    report = []
            else:
                report.append(line.strip())
    if report:
        yield report


def get_reports_AB(fn):
    end_1 = "-----------------------"
    end_2 = "End of metadata section"
    _start = False
    skip = True
    with open(fn) as fh:
        report = []
        prev_1 = False
        prev_2 = False
        for line in fh:
            if line.strip() == end_2:
                _start = True
            if line.strip() == end_1 and _start:
                skip = False
                continue
            if skip:
                continue
            if (
                (line.startswith("No") or line.startswith("Rapport"))
                and prev_1
                and prev_2
            ):
                if report:
                    yield report
                    report = []
            report.append(line.strip())
            if line.strip() == "":
                if prev_1:
                    prev_2 = True
                else:
                    prev_1 = True
            else:
                prev_1 = False
                prev_2 = False
    if report:
        yield report


def get_reports(fn):
    _fn = fn.split("/")[-1]
    if _fn.startswith("E"):
        yield from get_reports_E(fn)
    else:
        yield from get_reports_AB(fn)


def get_all_reports(data):
    reports = {}
    for fn in glob.glob(f"{data}/*txt"):
        metadata = get_metadata(fn)
        reports[fn] = {"metadata": metadata, "reports": []}
        for report in get_reports(fn):
            reports[fn]["reports"].append(report)
    return reports


if __name__ == "__main__":
    reports = get_all_reports(sys.argv[1])
    with open(sys.argv[2], "w") as fout:
        json.dump(reports, fout, indent=4)
