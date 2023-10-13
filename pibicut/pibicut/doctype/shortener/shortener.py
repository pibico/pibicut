# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator

from frappe import _, msgprint, throw
from frappe.utils import random_string, get_url

from pibicut.pibicut.custom import get_qrcode

class Shortener(WebsiteGenerator):
  def autoname(self):
    # select a project name based on customer
    random_code = random_string(5)
    doc = frappe.get_value("Shortener", {"short_url": random_code}, "name")
    if doc:
      frappe.throw(_("Try again, generated code is repeated on ") + doc.name)
    else:
      self.name = random_code
      self.short_url = self.name
    
  def validate(self):
    if not "http" in self.long_url:
      frappe.throw(_("Please enter a proper URL"))
      
  def before_save(self):
    url_short = "".join([self.name])
    qr_code = get_url(url_short)
    logo_files = frappe.get_all("File",
        fields=["name", "file_name", "file_url", "is_private"],
        filters={"attached_to_name": self.name, "attached_to_field": "logo",  "attached_to_doctype": "Shortener"},
    )
    logo = None
    if logo_files:
        print(logo_files)
        print(frappe.local.sites_path)
        logo = frappe.utils.get_files_path(logo_files[0].file_name, is_private=logo_files[0].is_private)

    self.qr_code = get_qrcode(qr_code, logo)
    self.published = True
    self.route = url_short
    #self.short_url = self.name
