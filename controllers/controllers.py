# -*- coding: utf-8 -*-
# from odoo import http


# class Ims(http.Controller):
#     @http.route('/ims/ims', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ims/ims/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ims.listing', {
#             'root': '/ims/ims',
#             'objects': http.request.env['ims.ims'].search([]),
#         })

#     @http.route('/ims/ims/objects/<model("ims.ims"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ims.object', {
#             'object': obj
#         })
