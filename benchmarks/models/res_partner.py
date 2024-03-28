from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bench_str: str = fields.Char(string='Bench String')
