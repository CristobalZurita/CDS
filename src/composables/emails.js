/**
 * Created by Ryan Balieiro on 03.05.2025
 * API integration with EmailJS for sending e-mails.
 */
import emailjs from "@emailjs/browser"
import {useSettings} from "/src/composables/settings.js"
import {useUtils} from "/src/composables/utils.js"

const settings = useSettings()
const utils = useUtils()

export const useEmails = () => {
    /**
     * @public
     */
    const init = () => {
        const credentials = settings.getCredentialsForEmailJS()
        emailjs.init(credentials.publicKey)
    }

    /**
     * @param {String} fromName
     * @param {String} fromEmail
     * @param {String} customSubject
     * @param {String} message
     * @return {Promise<boolean>}
     */
    const sendContact = async (fromName, fromEmail, customSubject, message) => {
        const params = {
            name: fromName,
            from_name: fromName,
            email: fromEmail,
            from_email: fromEmail,
            custom_subject: customSubject,
            message: message,
            custom_source: utils.getAbsoluteLocation(),
            custom_source_name: "Foxy Agency"
        }

        const credentials = settings.getCredentialsForEmailJS()

        try {
            const response = await emailjs.send(
                credentials.serviceId,
                credentials.templateId,
                params
            )
            return true
        } catch (error) {
            return false
        }
    }

    return {
        init,
        sendContact
    }
}