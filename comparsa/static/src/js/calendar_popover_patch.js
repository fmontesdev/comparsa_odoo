/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { CalendarCommonPopover } from "@web/views/calendar/calendar_common/calendar_common_popover";
import { is24HourFormat } from "@web/core/l10n/time";

// Muestra solo la hora de inicio en el popover del calendario (sin hora fin ni duración)
patch(CalendarCommonPopover.prototype, {
    computeDateTimeAndDuration() {
        super.computeDateTimeAndDuration(...arguments);
        if (this.time) {
            const { start } = this.props.record;
            const timeFormat = is24HourFormat() ? "HH:mm" : "hh:mm a";
            this.time = start.toFormat(timeFormat);
            this.timeDuration = null;
        }
    },
});
