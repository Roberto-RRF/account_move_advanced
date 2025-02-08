from odoo import models, fields
from odoo.exceptions import UserError

class XmlUploadWizard(models.TransientModel):
    _name = 'xml.upload.wizard'
    _description = 'XML Upload Wizard'

    file = fields.Binary('Archivo XML')
    file_name = fields.Char('Nombre Archivo')
    downloaded_xmls = fields.Many2one('account.edi.downloaded.xml.sat')

    move_id = fields.Many2one('account.move', string='Move', required=True)

    def action_submit(self):

        if self.file and self.downloaded_xmls:
            raise UserError("No puede seleccionar un XML de las descargas y, al mismo tiempo, subir un archivo.")
        
        if self.file:
        # Crea el attachment y lo captura en la variable 'attachment'
            attachment_id = self.env['ir.attachment'].create({
                'name': self.file_name,
                'datas': self.file,
                'res_model': 'account.move',
                'res_id': self.move_id.id,
                'mimetype': 'application/xml',
            })
        elif self.downloaded_xmls:
            attachment_id = self.downloaded_xmls.attachment_id
        else: 
            raise UserError("No se detectó ningún archivo seleccionado.")
        
        result = self.move_id.fill_xml_values_from_attatchment(attachment_id)
        if result:
            return result
        return {'type': 'ir.actions.act_window_close'}