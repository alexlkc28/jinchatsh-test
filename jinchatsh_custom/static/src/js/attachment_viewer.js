/** @odoo-module **/

import core from 'web.core';
import Widget from 'web.Widget';
import AttachmentViewer from '@mail_enterprise/js/attachment_viewer';

var JinchatshAttachmentViewer = Widget.extend(AttachmentViewer, {
    init: function (parent, attachments) {
        this._super.apply(this, arguments);
    },
});