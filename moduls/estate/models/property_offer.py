from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    price = fields.Float(string="Price")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], string="Status", default='pending', copy=False)

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property')
    property_type_id = fields.Many2one(
        'estate.property.type',
        string='Property Type',
        related='property_id.property_type_id',
        store=True
    )

    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    _sql_constraints = [
        ('price_positive', 'CHECK(price > 0)', 'Цена предложения должна быть строго положительной.'),
    ]

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.context_today(record)
            record.date_deadline = create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.context_today(record)
            record.validity = (record.date_deadline - create_date).days if record.date_deadline else 0

    def action_accept(self):
        for offer in self:
            if offer.status == 'accepted':
                raise UserError("Это предложение уже принято.")

            other_offers = self.search([('property_id', '=', offer.property_id.id), ('id', '!=', offer.id)])
            other_offers.write({'status': 'refused'})

            offer.status = 'accepted'

            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.state = 'offer_accepted'

    def action_refuse(self):
        for offer in self:
            if offer.status == 'refused':
                raise UserError("Это предложение уже отклонено.")
            offer.status = 'refused'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = vals.get('property_id')
            offer_price = vals.get('price')

            if property_id and offer_price:
                property_rec = self.env['estate.property'].browse(property_id)

                existing_prices = property_rec.offer_ids.mapped('price')
                if existing_prices and offer_price < max(existing_prices):
                    raise UserError("Нельзя создать предложение ниже уже существующего.")

                if property_rec.state == 'new':
                    property_rec.state = 'offer_received'

        return super().create(vals_list)
