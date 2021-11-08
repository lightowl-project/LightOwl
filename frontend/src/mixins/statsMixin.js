import moment from "moment"
import bytesIEC from "bytes-iec"

const statsMixin = {
  data: (vm) => ({
    predefineColors: [
      "#F49B51",
      "#ffd700",
      "#90ee90",
      "#00ced1",
      "#1e90ff",
      "#c71585",
      "#c7158577"
    ],
    maxDate: moment().format(),
    mappingDateRange: {
      "1m": vm.$t("Last minute"),
      "5m": vm.$t("Last 5 minutes"),
      "10m": vm.$t("Last 10 minutes"),
      "1h": vm.$t("Last hour"),
      today: vm.$t("Today"),
      yesterday: vm.$t("Yesterday"),
      "7d": vm.$t("Last 7 days"),
      "30d": vm.$t("Last 30 days"),
      "90d": vm.$t("Last 90 days")
    }
  }),

  computed: {
    dateStr() {
      if (this.selectedDate === "custom") {
        const format = this.formatDate(this.dateRange)
        const start = moment.utc(this.dateRange.startDate).format(format)
        const end = moment.utc(this.dateRange.endDate).format(format)
        return `${start} - ${end}`
      } else {
        return this.mappingDateRange[this.selectedDate]
      }
    }
  },

  mounted() {
  },

  methods: {
    selectDate(key, text) {
      this.selectedDate = key
      this.popoverDateOpen = false
    },
    zoom({ start, end }) {
      this.dateRange = { startDate: moment(start), endDate: moment(end) }
      this.selectedDate = "custom"
      this.$forceUpdate()
    },

    updateValues() {
      this.selectedDate = "custom"
    },

    calculateInterval(dateRange) {
      const start = moment.utc(dateRange.startDate)
      const end = moment.utc(dateRange.endDate)

      const duration = moment.duration((end).diff(start))
      // console.group("Duration")
      // console.log("Start date: ", start)
      // console.log("End date: ", end)
      // console.log("As Days: ", duration.asDays())
      // console.log("As Hours:", duration.asHours())
      // console.groupEnd()

      if (duration.asDays() > 31) {
        return "30d"
      } else if (duration.asDays() > 8) {
        return "7d"
      } else if (duration.asDays() > 1) {
        return "1d"
      } else if (duration.asHours() > 2) {
        return "1h"
      } else if (duration.asHours() >= 1) {
        return "10m"
      } else {
        return "1m"
      }
    },

    formatDate(dateRange) {
      const duration = this.calculateInterval(dateRange)
      switch (duration) {
        case "10m":
          return "HH:mm DD/MM/YYYY"
        case "1h":
          return "HH DD/MM/YYYY"
        case "1d":
          return "DD/MM/YYYY"
        case "7d":
          return "DD/MM/YYYY"
        case "30d":
          return "MM/YYYY"
      }

      return "HH:mm:ss DD/MM/YYYY"
    },

    getRelativeDate(value) {
      let startDate
      let endDate = new moment().utc()
      switch (value) {
        case "1m":
          startDate = new moment.utc().subtract(1, "minutes")
          break
        case "5m":
          startDate = new moment.utc().subtract(5, "minutes")
          break
        case "10m":
          startDate = new moment.utc().subtract(10, "minutes")
          break
        case "1h":
          startDate = new moment.utc().subtract(1, "hour")
          break
        case "today":
          startDate = new moment.utc().startOf("day")
          endDate = new moment.utc().endOf("day")
          break
        case "yesterday":
          startDate = new moment.utc().subtract(1, "day").startOf("day")
          endDate = new moment.utc().subtract(1, "day").endOf("day")
          break
        case "7d":
          startDate = new moment.utc().subtract(7, "day").startOf("day")
          break
        case "30d":
          startDate = new moment.utc().subtract(30, "day").startOf("day")
          break
        case "90d":
          startDate = new moment.utc().subtract(30, "day").startOf("day")
          break
      }

      return {
        startDate: startDate,
        endDate: endDate
      }
    },

    formatVal(value, data_type) {
      switch (data_type) {
        case "gb":
          value = (value / (1000 * 1000 * 1000)).toFixed(2)
          break
        case "kb":
          value = (value / (1000 * 1000)).toFixed(2)
          break
      }

      return value
    },

    formatBytes(bytes, decimals = 2) {
      return bytesIEC(bytes, { mode: "binary" })
    },

    formatValues(values, convert) {
      const serie = []
      for (const tmp of values) {
        const date = moment.utc(tmp[0])
        let value = tmp[1].toFixed(2)

        if (convert) {
          if (convert.operator === "div") {
            value = value / convert.value
          }
        }

        serie.push([date, value])
      }

      return serie
    },

    formatTimeSeries(param, data, convert) {
      const datasets = []

      if (!param.group_by) {
        for (const field of param.fields) {
          let values = []
          try {
            values = data[`${param.measurement}.${field}`].series[0].values
          } catch (err) { }

          const serie = this.formatValues(values)
          datasets.push({ name: field, data: serie })
        }
      } else {
        const field = param.fields[0]
        const group_by = param.group_by
        const series = data[`${param.measurement}.${field}`].series

        for (const tmp_serie of series) {
          const serie_name = tmp_serie.tags[group_by]
          const serie = this.formatValues(tmp_serie.values, convert)
          datasets.push({ name: serie_name, data: serie })
        }
      }

      return datasets
    }
  }
}

export default statsMixin
