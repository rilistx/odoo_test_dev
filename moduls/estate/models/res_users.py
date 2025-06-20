from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    selling_price = fields.Float(string="Selling Price")

    estate_property_ids = fields.One2many(
        'estate.property',
        'seller_id',
        string='Properties',
    )
