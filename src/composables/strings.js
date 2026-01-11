/**
 * Created by Ryan Balieiro on 03.01.2025
 */
const MAP = {
    "about": "About",
    "all_categories": "All",
    "contact_thank_you": "*Thank you* for getting in touch!",
    "contact_thank_you_description": "Your message has been received, and our team will be in touch with you shortly.",
    "contact_thank_you_reply": "Our reply will be sent to your email address *{email}*.",
    "copyright_message": "Copyright ©{year} <a href='{url}' target='_blank'>{holder}</a> – {license}",
    "email": "E-mail",
    "error_fill_all_fields": "Please fill all the fields.",
    "error_invalid_email": "Please enter a valid e-mail address.",
    "error_sending_message": "There was an error sending the message.",
    "latest_release": "Novedades",
    "loading": "Loading...",
    "message": "Message",
    "name": "Name",
    "project_available_here": "<strong>@{title}</strong> is available on the following platforms or services:",
    "send": "Send Message",
    "sending_message": "Sending Message...",
    "subject": "Subject",
    "tags": "Tags:",
    "where_to_find": "Where To Find"
}

export function useStrings() {
    /**
     * @param {String} key
     * @param {{key:String, replacement:String}[]} [replacements=null]
     * @return {*|string}
     */
    const get = (key, replacements) => {
        let string = MAP[key] || 'strings.' + key

        if(replacements) {
            replacements.forEach(({key, replacement}) => {
                string = string.replaceAll('@{'+key+'}', replacement)
            })
        }

        return string
    }

    /**
     * @param {String|Number} year
     * @param {String} holder
     * @param {String} url
     * @return {string}
     */
    const getCopyrightMessage = (year, holder, url, license) => {
        return get("copyright_message").replaceAll("{year}", year.toString())
            .replaceAll("{url}", url)
            .replaceAll("{holder}", holder)
            .replaceAll("{license}", license)
    }

    return {
        get,
        getCopyrightMessage
    }
}