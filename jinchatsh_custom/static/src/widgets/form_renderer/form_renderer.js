/** @odoo-module **/

import '@mail_enterprise/widgets/form_renderer/form_renderer';
import JinchatshAttachmentViewer from '@jinchatsh_custom/js/attachment_viewer';

FormRenderer.include({
    init: function () {
        this._super.apply(this, arguments);
        console.log('jinchatsh form_render');
    }
});