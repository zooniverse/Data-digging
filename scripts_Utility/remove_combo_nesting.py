#!/usr/bin/env python

import csv
import json
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Undo nesting of annotations for combo task")
    parser.add_argument("--classification_export", required=True,
                        help="Input Filename of Classification Export CSV")
    parser.add_argument("--combo_task_id", required=True, help="Task ID for Combo Task")
    parser.add_argument("--output_file", required=True, help="Output Filename for CSV")

    args = parser.parse_args()
    file_input = args.classification_export
    file_output = args.output_file
    combo_task_id = args.combo_task_id

    with open(file_output, 'w') as csvout:
        with open(file_input) as csvin:
            classifications = csv.DictReader(csvin)
            writer = csv.DictWriter(csvout, classifications.fieldnames)
            writer.writeheader()
            for c in classifications:
                annotations = json.loads(c['annotations'])
                for a in annotations: 
                    if a['task'] == combo_task_id: 
                        for t in a['value']: 
                            annotations.append(t) 
                        annotations.remove(a)
                c['annotations']=annotations
                writer.writerow(c)
