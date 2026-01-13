export class SectionInfo {
  constructor(id, component, data = null, options = null) {
    this.id = id
    this.component = component
    this.data = data
    this.options = options || {}
  }
}
