/** @odoo-module **/

import config from 'web.config';
import dom from 'web.dom';
import pyUtils from 'web.py_utils';
import FormRenderer from '@mail_enterprise/widgets/form_renderer/form_renderer';
import JinchatshAttachmentViewer from '@jinchatsh_custom/js/attachment_viewer';

FormRenderer.include({
    init: function () {
        this._super.apply(this, arguments);
        console.log('jinchatsh form_render');
    }
});