frappe.listview_settings['Shortener'] = {
    hide_name_column: true,

    get_indicator: function(doc) {
        // Show "Expired" indicator for expired links
        if (doc.expires_on && new Date(doc.expires_on) < new Date()) {
            return [__("Expired"), "red", "expires_on,<,Today"];
        }
        return [__("Active"), "green", ""];
    },

    onload: function(listview) {
        // Add bulk actions
        listview.page.add_action_item(__('Export QR Codes (ZIP)'), function() {
            let selected = listview.get_checked_items();
            if (selected.length === 0) {
                frappe.msgprint(__('Please select at least one item'));
                return;
            }

            let names = selected.map(d => d.name);

            frappe.call({
                method: 'pibicut.pibicut.api.export_qr_codes_zip',
                args: { names: names },
                callback: function(r) {
                    if (r.message && r.message.file_url) {
                        window.open(r.message.file_url);
                        frappe.show_alert({
                            message: __('QR codes exported successfully!'),
                            indicator: 'green'
                        });
                    }
                }
            });
        });

        listview.page.add_action_item(__('Copy All URLs'), function() {
            let selected = listview.get_checked_items();
            if (selected.length === 0) {
                frappe.msgprint(__('Please select at least one item'));
                return;
            }

            let urls = selected.map(d => window.location.origin + '/' + d.name);
            let text = urls.join('\n');

            navigator.clipboard.writeText(text).then(() => {
                frappe.show_alert({
                    message: __('All URLs copied to clipboard!'),
                    indicator: 'green'
                });
            }).catch(() => {
                // Fallback
                let temp = document.createElement('textarea');
                temp.value = text;
                document.body.appendChild(temp);
                temp.select();
                document.execCommand('copy');
                document.body.removeChild(temp);
                frappe.show_alert({
                    message: __('All URLs copied to clipboard!'),
                    indicator: 'green'
                });
            });
        });
    },

    button: {
        show: function(doc) {
            return true;
        },
        get_label: function() {
            return __('Copy');
        },
        get_description: function(doc) {
            return __('Copy short URL to clipboard');
        },
        action: function(doc) {
            let url = window.location.origin + '/' + doc.name;
            navigator.clipboard.writeText(url).then(() => {
                frappe.show_alert({
                    message: __('URL copied: {0}', [url]),
                    indicator: 'green'
                });
            }).catch(() => {
                let temp = document.createElement('textarea');
                temp.value = url;
                document.body.appendChild(temp);
                temp.select();
                document.execCommand('copy');
                document.body.removeChild(temp);
                frappe.show_alert({
                    message: __('URL copied: {0}', [url]),
                    indicator: 'green'
                });
            });
        }
    }
};
