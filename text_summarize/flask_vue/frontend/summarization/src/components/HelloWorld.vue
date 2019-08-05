<template>
  <v-container>
    <v-layout
      text-center
      wrap
    >
      <v-flex 
        mb-6
        xs12
      ></v-flex>

      <v-flex mb-4>
        <h1 class="display-2 font-weight-bold mb-3">
          Automatic Summarization
        </h1>
        <p class="subheading font-weight-regular">
          A simple automatic summarization based on textrank and word-vector
        </p>
      </v-flex>

    <v-container fluid grid-list-md>
      <v-textarea
        label="please input text"
        v-model="text"
      ></v-textarea>
    </v-container>

    <v-container fluid grid-list-md>
    <v-btn class="ma-2" outlined color="indigo" v-on:click="generate">Generate</v-btn>
    </v-container>

    <div class="text-center" v-show="!hidden">
      <span>Keywords</span>
      <v-chip
        class="ma-2"
        v-for='kv in keywords' v-bind:key="kv.id"
      >
      {{ kv }}
      </v-chip>
    </div>

    <v-flex 
      mb-6
      xs12
    ></v-flex>

    <div class="text-left" v-show="!hidden">
      <span>summarization</span>
      <v-chip
        class="ma-2"
        v-for='kv in summa' v-bind:key="kv.id"
      >
      {{ kv }}
      </v-chip>
    </div>

    </v-layout>

  </v-container>
</template>

<script>
export default {
  data: () => ({
    hidden: true,
    text: "自动摘要是使用软件缩短文本文档的过程，以便创建包含原始文档主要点的摘要。\
可以进行连贯性总结的技术会考虑诸如长度，书写风格和语法等变量。",
    keywords: [],
    summa: []
  }),

  methods: {
    generate: function() {
      var self = this

      this.axios.post('http://localhost:5000/generate', {
        text: this.text
      })
      .then(function (response) {
        self.keywords = response.data.keywords
        self.summa = response.data.summa
        self.hidden = false
      })
      .catch(function (){
        alert("error")
      })
    }
  }
};
</script>
