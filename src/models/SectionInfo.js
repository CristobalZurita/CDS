export default class SectionInfo {
    /**
     * @param {String} id
     * @param {*} component
     * @param {String} name
     * @param {String} faIcon
     */
    constructor(id, component, name = "", faIcon= "") {
        this._id = id
        this._component = component
        if(!this._id || !this._component) {
            throw new Error("You must specify an ID and a component for every SectionInfo object!")
        }

        this._name = name
        this._faIcon = faIcon
    }

    get id() {
        return this._id
    }

    get name() {
        return this._name || null
    }

    get faIcon() {
        return this._faIcon || "fa-solid fa-circle"
    }

    get component() {
        return this._component
    }

    get hash() {
        return `#${this.id}`
    }
}