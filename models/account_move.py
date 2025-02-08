from odoo import models, fields
from odoo.exceptions import UserError
import xml.etree.ElementTree as ET
import base64
from odoo.addons.l10n_mx_edi.models.l10n_mx_edi_document import USAGE_SELECTION

class CustomAccountMove(models.Model):
    _inherit = 'account.move'

    cfdi_payment_method = fields.Char("Método de Pago", 
                                      help="Valor agregado por el botón verde")
    cfdi_payment_form = fields.Many2one('l10n_mx_edi.payment.method', 
                                        "Forma de Pago", 
                                        help="Valor agregado por el botón verde")
    cfdi_usgae = fields.Selection(USAGE_SELECTION, 
                                  string="Uso CFDI", 
                                  help="Valor agregado por el botón verde")
    wizard_imported = fields.Boolean("Wizard Imported")

    def action_open_upload_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'XML Upload Wizard',
            'res_model': 'xml.upload.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_move_id': self.id},
        }

    def action_erase_fields(self):
        self.cfdi_payment_method = ""
        self.cfdi_payment_form = ""
        self.cfdi_usgae = ""
        self.l10n_mx_edi_document_ids.unlink()
        self.wizard_imported = False

    def fill_xml_values_from_attatchment(self, attachment):
        edi_document_obj = self.env['l10n_mx_edi.document']
        edi_content = attachment

        # Crear el registro del documento EDI
        edi_data = {
            'state': 'invoice_sent',
            'datetime': fields.Datetime.now(),
            'attachment_id': edi_content.id,
            'move_id': self.id,
        }
        new_edi_doc = edi_document_obj.create(edi_data)
        new_edi_doc.invoice_ids = [(6, 0, [self.id])]

        # Decodificar el XML
        decoded_xml = base64.b64decode(edi_content.datas)
        cfdi_node = edi_document_obj._decode_cfdi_attachment(decoded_xml)
        root = ET.fromstring(decoded_xml)

        tipo_comprobante = root.get('TipoDeComprobante')
        if tipo_comprobante not in ('I', 'E'):
            raise UserError(
                "El XML debe ser de tipo Ingreso (I) o Egreso (E). Se encontró: %s" % tipo_comprobante
            )

        try:
            # Asignar campos básicos desde el XML
            self.cfdi_payment_method = cfdi_node.get('payment_method')
            self.cfdi_payment_form = self.env['l10n_mx_edi.payment.method'].search([
                ('code', '=', root.get('FormaPago'))
            ])
            self.cfdi_usgae = cfdi_node.get('usage')
            self.wizard_imported = True

            # Validación modificada
            errors = self._validate_invoice_xml_data(root, cfdi_node)
            if errors:
                if not self.env.context.get('bypass_validation'):
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Confirmar Validación',
                        'res_model': 'custom.validation.confirm',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {
                            'default_move_id': self.id,
                            'default_attachment_id': attachment.id,
                            'default_errors': '\n'.join(errors),
                        },
                    }
                else:
                    self.message_post(body="Advertencias de validación: %s" % '\n'.join(errors))

            # Resto del código si la validación es exitosa
            self._validate_invoice_xml_data(root, cfdi_node)

        except Exception as e:
            raise UserError("Error: %s" % str(e))

    def _validate_invoice_xml_data(self, root, cfdi_node):
        errors = []
        xml_rfc = cfdi_node.get('supplier_rfc')
        xml_amount_total = float(cfdi_node.get('amount_total'))
        xml_amount_subtotal = float(root.get('SubTotal'))

        # if self.partner_id.vat != xml_rfc:
        #     raise UserError("El RFC del proveedor en la factura (%s) no coincide con el RFC del XML (%s)." % (self.partner_id.vat, xml_rfc))

        if round(self.amount_untaxed, 2) != round(xml_amount_subtotal, 2):
            errors.append("El subtotal de la factura (%.2f) no coincide con el subtotal indicado en el XML (%.2f)." % (self.amount_untaxed, xml_amount_subtotal))

        # if round(self.amount_total, 2) != round(xml_amount_total, 2):
        #     raise UserError("El total de la factura (%.2f) no coincide con el total indicado en el XML (%.2f)." % (self.amount_total, xml_amount_total))

        return errors