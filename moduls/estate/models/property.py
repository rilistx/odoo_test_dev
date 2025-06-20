from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(string="Title", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    expected_price = fields.Float(string="Expected Price", required=True)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    availability_date = fields.Date(
        string="Availability Date",
        default=lambda self: fields.Date.context_today(self) + timedelta(days=90),
        copy=False
    )
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='new', required=True, copy=False)
    zip = fields.Char(string="Zip")

    property_type_id = fields.Many2one(
        'estate.property.type',
        string='Property Type',
        options={'no_create': True, 'no_open': True},
    )

    tag_ids = fields.Many2many(
        'estate.property.tag',
        string='Tags',
        options={'color_field': 'color'},
    )
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    seller_id = fields.Many2one('res.users', string='Seller', default=lambda self: self.env.user)
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    living_area = fields.Integer(string="Living Area")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area")
    orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ], string="Garden Orientation")

    total_area = fields.Integer(string="Total Area", compute="_compute_total_area", store=True)
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price", store=True)

    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price > 0)', 'Ожидаемая цена должна быть строго положительной.'),
        ('selling_price_positive', 'CHECK(selling_price >= 0)', 'Цена продажи должна быть неотрицательной.'),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.orientation = 'north'
        else:
            self.garden_area = 0
            self.orientation = False

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Проданную недвижимость нельзя отменить.")
            record.state = 'cancelled'

    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Отменённую недвижимость нельзя продать.")
            if not record.buyer_id or not record.selling_price:
                raise UserError("Для продажи необходимо указать покупателя и цену продажи.")
            record.state = 'sold'

    @api.ondelete(at_uninstall=False)
    def _check_state_before_delete(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise ValidationError("Удалять можно только объекты в статусе 'New' или 'Cancelled'.")
