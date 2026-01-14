// Copyright (c) 2021, PibiCo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shortener', {
    refresh(frm) {
        // Show QR preview
        if (!frm.doc.__islocal && frm.doc.qr_code) {
            let template = `<img src="${frm.doc.qr_code}" width="240px" style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"/>`;
            frm.set_df_property('qr_preview', 'options', template);
            frm.refresh_field('qr_preview');

            // Show short URL prominently
            let short_url = window.location.origin + '/' + frm.doc.name;
            let url_html = `
                <div style="margin-bottom: 10px;">
                    <a href="${short_url}" target="_blank" style="font-size: 16px; font-weight: bold; color: var(--primary-color);">
                        ${short_url}
                    </a>
                </div>
            `;
            frm.set_df_property('short_url_display', 'options', url_html);
            frm.refresh_field('short_url_display');

            // Copy URL button
            let copy_html = `
                <button class="btn btn-primary btn-sm copy-url-btn" style="margin-right: 8px;">
                    <i class="fa fa-copy"></i> ${__('Copy URL')}
                </button>
            `;
            frm.set_df_property('copy_url_html', 'options', copy_html);
            frm.refresh_field('copy_url_html');

            // Add copy button click handler
            setTimeout(() => {
                $(frm.fields_dict.copy_url_html.$wrapper).find('.copy-url-btn').on('click', function() {
                    navigator.clipboard.writeText(short_url).then(() => {
                        frappe.show_alert({
                            message: __('URL copied to clipboard!'),
                            indicator: 'green'
                        });
                    }).catch(() => {
                        // Fallback for older browsers
                        let temp = document.createElement('textarea');
                        temp.value = short_url;
                        document.body.appendChild(temp);
                        temp.select();
                        document.execCommand('copy');
                        document.body.removeChild(temp);
                        frappe.show_alert({
                            message: __('URL copied to clipboard!'),
                            indicator: 'green'
                        });
                    });
                });
            }, 100);

            // QR download button
            let download_html = `
                <button class="btn btn-secondary btn-sm download-qr-btn">
                    <i class="fa fa-download"></i> ${__('Download QR Code')}
                </button>
            `;
            frm.set_df_property('qr_download_html', 'options', download_html);
            frm.refresh_field('qr_download_html');

            // Add download button click handler
            setTimeout(() => {
                $(frm.fields_dict.qr_download_html.$wrapper).find('.download-qr-btn').on('click', function() {
                    let link = document.createElement('a');
                    link.download = `qr-${frm.doc.name}.png`;
                    link.href = frm.doc.qr_code;
                    link.click();
                    frappe.show_alert({
                        message: __('QR Code downloaded!'),
                        indicator: 'green'
                    });
                });
            }, 100);
        } else {
            // New document - clear displays
            frm.set_df_property('qr_preview', 'options', '');
            frm.set_df_property('short_url_display', 'options', '');
            frm.set_df_property('copy_url_html', 'options', '');
            frm.set_df_property('qr_download_html', 'options', '');
            frm.refresh_fields(['qr_preview', 'short_url_display', 'copy_url_html', 'qr_download_html']);
        }
    },

    onload(frm) {
        // Initialize URL status
        if (frm.doc.__islocal) {
            frm.set_df_property('url_status', 'options', '');
            frm.refresh_field('url_status');
        }
    },

    long_url(frm) {
        // Real-time URL validation
        if (!frm.doc.long_url) {
            frm.set_df_property('url_status', 'options', '');
            frm.refresh_field('url_status');
            return;
        }

        // Show loading
        frm.set_df_property('url_status', 'options', `
            <span style="color: var(--text-muted);">
                <i class="fa fa-spinner fa-spin"></i> ${__('Validating URL...')}
            </span>
        `);
        frm.refresh_field('url_status');

        // Validate URL via API
        frappe.call({
            method: 'pibicut.pibicut.api.validate_url',
            args: { url: frm.doc.long_url },
            callback: function(r) {
                if (r.message && r.message.valid) {
                    frm.set_df_property('url_status', 'options', `
                        <span style="color: var(--green-500);">
                            <i class="fa fa-check-circle"></i> ${__('Valid URL')}
                        </span>
                    `);
                } else {
                    frm.set_df_property('url_status', 'options', `
                        <span style="color: var(--red-500);">
                            <i class="fa fa-times-circle"></i> ${r.message ? r.message.message : __('Invalid URL')}
                        </span>
                    `);
                }
                frm.refresh_field('url_status');
            }
        });
    },

    custom_code(frm) {
        // Check custom code availability
        if (!frm.doc.custom_code) return;

        // Validate format first
        let code = frm.doc.custom_code;
        if (!/^[a-zA-Z0-9\-]{3,20}$/.test(code)) {
            frappe.show_alert({
                message: __('Custom code must be 3-20 characters, using only letters, numbers, and hyphens'),
                indicator: 'orange'
            });
            return;
        }

        // Check availability
        frappe.call({
            method: 'pibicut.pibicut.api.check_custom_code',
            args: { code: code },
            callback: function(r) {
                if (r.message && !r.message.available) {
                    frappe.show_alert({
                        message: __('This custom code is already taken'),
                        indicator: 'red'
                    });
                } else if (r.message && r.message.available) {
                    frappe.show_alert({
                        message: __('Custom code is available!'),
                        indicator: 'green'
                    });
                }
            }
        });
    }
});
