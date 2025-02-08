from odoo import models, fields, api

class CustomValidationConfirm(models.TransientModel):
    _name = 'custom.validation.confirm'
    _description = 'Confirmar Validación'

    move_id = fields.Many2one('account.move', required=True)
    attachment_id = fields.Many2one('ir.attachment', required=True)
    errors = fields.Text('Errores')

    def action_confirm(self):
        self.ensure_one()
        # Llama al método original con bandera de bypass
        self.move_id.with_context(bypass_validation=True).fill_xml_values_from_attatchment(self.attachment_id)
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        self.move_id.action_erase_fields()
        return {'type': 'ir.actions.act_window_close'}