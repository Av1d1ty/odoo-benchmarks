import timeit
from typing import Tuple
from textwrap import dedent
from odoo.tests import common


class TestModelA(common.TransactionCase):
    def test_some_action(self):
        self.globals_vals = {'env': self.env}
        self.setup = "records = env['res.partner'].search([])"
        self.repetitions = (1, 10, 100)

        for repetition in self.repetitions:
            code_slow, code_fast = loop_vs_map()
            slow_time = timeit.repeat(
                code_slow,
                setup=self.setup,
                number=repetition,
                globals=self.globals_vals
            )
            fast_time = timeit.repeat(
                code_fast,
                setup=self.setup,
                number=repetition,
                globals=self.globals_vals
            )
            print(f'\n=============== loops {repetition}')
            print([format(f, f".{5}f") for f in slow_time])
            print([format(f, f".{5}f") for f in fast_time])
        print()


def field_settings_vs_write() -> Tuple[str, str]:   # PERF: 10x speedup
    code_slow = "for rec in records: rec.bench_str = 'benchmark'"
    code_fast = "records.write({'bench_str': 'benchmark'})"
    return code_slow, code_fast


def set_vs_recordset() -> Tuple[str, str]:   # PERF: 10x speedup
    code_slow = dedent("""
        result = env['res.partner'].browse()
        for record in records:
            result |= record
    """)
    code_fast = dedent("""
        result = set()
        for record in records:
            result.add(record.id)
        env['res.partner'].browse(result)
    """)
    return code_slow, code_fast


def loop_vs_filtered() -> Tuple[str, str]:   # PERF: no speedup
    code_slow = dedent("""
        partners_start_with_a = set()
        for record in records:
            if record.name.lower().startswith('a'):
                partners_start_with_a.add(record.id)
        env['res.partner'].browse(partners_start_with_a)
    """)
    code_fast = dedent("""
        records.filtered(lambda r: r.name.lower().startswith('a'))
    """)
    return code_slow, code_fast


def signle_vs_multi_browse() -> Tuple[str, str]:   # PERF: 2x speedup
    code_slow = dedent("""
        record_ids = records.ids
        for record_id in record_ids:
            record = env['res.partner'].browse(record_id)
            record.name
    """)
    code_fast = dedent("""
        record_ids = records.ids
        for record in env['res.partner'].browse(record_ids):
            record.name
    """)
    return code_slow, code_fast


def loop_vs_map() -> Tuple[str, str]:   # PERF: 2x speedup
    code_slow = dedent("""
        def increment_id(record_id):
            return record_id + 1
        for record_id in records.ids:
            increment_id(record_id)
    """)
    code_fast = dedent("""
        def increment_id(record_id):
            return record_id + 1
        map(increment_id, records.ids)
    """)
    return code_slow, code_fast
