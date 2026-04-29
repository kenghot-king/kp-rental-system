/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class RentalSerialImportDialog extends Component {
    static template = "ggg_rental.RentalSerialImportDialog";
    static components = { Dialog };
    static props = {
        close: Function,
    };

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            uploading: false,
            result: null,
            fileName: "",
        });
    }

    onFileChange(ev) {
        const file = ev.target.files[0];
        this.state.fileName = file ? file.name : "";
        this._file = file || null;
    }

    async onUpload() {
        if (!this._file) {
            this.notification.add(_t("Please select a CSV file"), { type: "warning" });
            return;
        }

        this.state.uploading = true;
        try {
            const formData = new FormData();
            formData.append("file", this._file);

            const response = await fetch("/ggg_rental/import_serials", {
                method: "POST",
                body: formData,
            });
            this.state.result = await response.json();
        } catch (e) {
            this.state.result = { error: e.message || "Upload failed" };
        }
        this.state.uploading = false;
    }
}
