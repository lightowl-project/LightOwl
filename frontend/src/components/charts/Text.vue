<template>
  <el-result :style="backgroundStyle">
    <template slot="icon">
      <h1 :style="titleStyle">{{ title }}</h1>
    </template>
    <template slot="extra">
      <span :style="valueStyle" class="bonsoir" v-html="displayText()" />
    </template>
  </el-result>
</template>

<script>
export default {
  components: {},
  props: {
    title: {
      type: String,
      default: ""
    },
    options: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    datacollection: {}
  }),
  computed: {
    backgroundStyle() {
      return {
        "background-color": this.options.text.background.color,
        height: "100%"
      }
    },
    titleStyle() {
      return {
        "font-size": `${this.options.text.title.fontSize}px !important`,
        color: this.options.text.color,
        padding: "0 !important",
        margin: "0 !important"
      }
    },
    valueStyle() {
      return {
        "font-size": `${this.options.text.value.fontSize}px !important`,
        color: this.options.text.color
      }
    }
  },

  beforeMount() {
    if (this.options.text.convertToInt) {
      this.datacollection = parseInt(this.datacollection)
    } else {
      this.datacollection = parseFloat(this.datacollection)
    }

    if (!this.options.text.color) {
      this.options.text.color = "#000"
    }
  },

  methods: {
    displayText() {
      if (this.options.text.value_mapping.length === 0) {
        return this.datacollection
      }

      for (const value_mapping of this.options.text.value_mapping) {
        if (this.options.text.convertToInt) {
          value_mapping.pattern = parseInt(value_mapping.pattern)
        } else {
          value_mapping.pattern = parseFloat(value_mapping.pattern)
        }

        switch (value_mapping.operator) {
          case "eq":
            if (this.datacollection === value_mapping.pattern) {
              return value_mapping.display
            }
            break
          case "lt":
            if (this.datacollection < value_mapping.pattern) {
              return value_mapping.display
            }
            break
          case "lte":
            if (this.datacollection <= value_mapping.pattern) {
              return value_mapping.display
            }
            break
          case "gt":
            if (this.datacollection > value_mapping.pattern) {
              return value_mapping.display
            }
            break
          case "gte":
            if (this.datacollection >= value_mapping.pattern) {
              return value_mapping.display
            }
            break
        }
      }
    },

    updateSeries(series) {
      this.datacollection = series
      this.$forceUpdate()
    },

    updateOptions() {}
  }
}
</script>
