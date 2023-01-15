# -*- coding: utf-8 -*-
# from odoo import http


# class GlossyElements(http.Controller):
#     @http.route('/glossy_elements/glossy_elements/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/glossy_elements/glossy_elements/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('glossy_elements.listing', {
#             'root': '/glossy_elements/glossy_elements',
#             'objects': http.request.env['glossy_elements.glossy_elements'].search([]),
#         })

#     @http.route('/glossy_elements/glossy_elements/objects/<model("glossy_elements.glossy_elements"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('glossy_elements.object', {
#             'object': obj
#         })
