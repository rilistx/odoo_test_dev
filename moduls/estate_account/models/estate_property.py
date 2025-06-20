from odoo import models, fields, api
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_set_sold(self):
        res = super().action_set_sold()

        for property in self:
            if not property.buyer_id:
                raise UserError("Покупатель не указан, невозможно создать счет.")

            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            if not journal:
                raise UserError("Журнал для продаж не найден.")

            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': property.buyer_id.id,
                'invoice_date': fields.Date.context_today(self),
                'journal_id': journal.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'name': f'Продажа недвижимости: {property.name}',
                        'quantity': 1,
                        'price_unit': property.selling_price * 0.06,
                    }),
                    (0, 0, {
                        'name': 'Административные сборы',
                        'quantity': 1,
                        'price_unit': 100.00,
                    }),
                ],
            }

            invoice = self.env['account.move'].create(invoice_vals)

        return res
