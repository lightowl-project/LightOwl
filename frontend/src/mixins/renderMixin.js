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

    render_asset_label(agent) {
      return `${agent.ip_address} - ${agent.hostname}`
    },

    renderUPtime(uptime_seconds) {
      const uptime_moment = moment.duration({ seconds: uptime_seconds })

      let uptime = ""
      if (uptime_moment.days()) {
        uptime = `${uptime_moment.days()} days `
      }

      if (uptime_moment.hours()) {
        uptime = `${uptime}${uptime_moment.hours()}h `
      }

      uptime = `${uptime}${uptime_moment.minutes()}m ${uptime_moment.seconds()}s`
      return uptime
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
