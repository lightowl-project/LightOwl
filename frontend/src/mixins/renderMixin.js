import moment from "moment"

const renderMixin = {
  methods: {
    renderDate(date) {
      const f = "DD/MM/YYYY HH:mm:ss"
      const m = moment.utc(date).format(f)
      if (m === "Invalid date") { return "<i class='fa fa-ban'></i>" }
      return m
    },

    renderImage(img) {
      return `data:image/png;base64,${img}`
    },

    renderDialogWidth() {
      const windowSize = window.innerWidth
      let size = "60%"

      if (windowSize < 2000) size = "80%"
      if (windowSize < 1000) size = "100%"

      return size
    },

    renderIcon(icon, size) {
      const s = size === "large" ? "fa-4x" : "mr-1"
      return `${icon} ${s}`
    },

    renderTagPriority(priority) {
      const mapping = {
        1: "danger",
        2: "high",
        3: "medium",
        4: "low",
        5: "info"
      }

      return mapping[priority]
    },

    renderOSIcon(os, classes) {
      const mapping = {
        "linux": "fab fa-linux",
        "macos": "fab fa-apple",
        "windows": "fab fa-windows"
      }

      return `${mapping[os.toLowerCase()]} ${classes}`
    }

  }
}

export default renderMixin
