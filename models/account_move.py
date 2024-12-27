from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
import xml.etree.ElementTree as ET
import base64
from odoo.addons.l10n_mx_edi.models.l10n_mx_edi_document import USAGE_SELECTION



class CustomAccountMove(models.Model):
    _inherit = 'account.move'

    cfdi_payment_method = fields.Char("Metodo de Pago")
    cfdi_payment_form = fields.Many2one('l10n_mx_edi.payment.method', "Forma de Pago")
    cfdi_usgae = fields.Selection(USAGE_SELECTION, string="Uso CFDI")
    wizard_imported = fields.Boolean("Wizard Imported")
    def action_open_upload_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'XML Upload Wizard',
            'res_model': 'xml.upload.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_move_id': self.id,
            },
        }
    
    def fill_xml_values_from_attatchment(self):
        edi = self.env['l10n_mx_edi.document']
        edi_content = self.attachment_ids.filtered(lambda m: m.mimetype == 'application/xml')
        if edi_content:

            edi_data = {
                'state' : 'invoice_sent',
                'datetime': fields.Datetime.now(),
                'attachment_id':edi_content.id,
                'move_id': self.id,
            }
            new_edi_doc = edi.create(edi_data)
            new_edi_doc.invoice_ids = [(6, 0, [self.id])]

            cfdi_node = self.env['l10n_mx_edi.document']._decode_cfdi_attachment(edi_content.raw)
            if cfdi_node.get('uuid'):
                if self.env['account.move'].search([('l10n_mx_edi_cfdi_uuid','=',cfdi_node.get('uuid'))], limit=1):
                    raise UserError("Ya existe una factura con ese mismo XML")
            root = ET.fromstring(base64.b64decode(edi_content.datas))
            
            ref = (root.get('Serie') + '/' if root.get('Serie') else '') + (root.get('Folio') if root.get('Folio') else '')
            self.ref = ref
            self.invoice_date = cfdi_node.get('stamp_date')
            self.cfdi_payment_method = cfdi_node.get('payment_method')
            self.cfdi_payment_form = self.env['l10n_mx_edi.payment.method'].search([('code','=',root.get('FormaPago'))])
            self.cfdi_usgae = cfdi_node.get('usage')
            self. wizard_imported = True
            # raise UserError("A")
            
