from odoo import models, fields
from odoo.exceptions import UserError

class XmlUploadWizard(models.TransientModel):
    _name = 'xml.upload.wizard'
    _description = 'XML Upload Wizard'

    file = fields.Binary('Archivo XML')
    file_name = fields.Char('Nombre Archivo')

    move_id = fields.Many2one('account.move', string='Move', required=True)

    def action_submit(self):
        attachment_values = {
            'name': self.file_name, 
            'datas': self.file,
            'res_model': 'account.move',
            'res_id': self.move_id.id,
            'mimetype': 'application/xml',
        }
        self.env['ir.attachment'].create(attachment_values)
        self.move_id.fill_xml_values_from_attatchment()
        return