// Copyright (c) 2021, PibiCo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shortener', {
  refresh(frm) {
    var template = '';
    
    if (frm.doc.__islocal) {
      template = '<img src="" />';
	    frm.set_df_property('qr_preview', 'options', frappe.render_template(template));
      frm.refresh_field('qr_preview');
    } else {
      /*
      if (frm.doc.logo) {
	      frm.set_df_property('logo', 'read_only', 1);    
	      frm.refresh_field('logo');
      } else {
        frm.set_df_property('logo', 'hidden', 1);    
	      frm.refresh_field('logo');  
      }
      */
      template = '<img src="' + frm.doc.qr_code + '" width="240px"/>';
	    frm.set_df_property('qr_preview', 'options', frappe.render_template(template));
      frm.refresh_field('qr_preview');
    }
  },
  onload(frm) {
    var template = '';
    if (frm.doc.__islocal) {
      template = '<img src="" />';
	    frm.set_df_property('qr_preview', 'options', frappe.render_template(template));
      frm.refresh_field('qr_preview');
    } else {
      /*
      if (frm.doc.logo) {
	      frm.set_df_property('logo', 'read_only', 1);    
	      frm.refresh_field('logo');
      } else {
        frm.set_df_property('logo', 'hidden', 1);    
	      frm.refresh_field('logo');  
      }
      */
      template = '<img src="' + frm.doc.qr_code + '" width="240px"/>';
	    frm.set_df_property('qr_preview', 'options', frappe.render_template(template));
      frm.refresh_field('qr_preview');
    }
  }
});
