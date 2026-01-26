<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'app',
};
</script>

<style lang="scss">
  // Import Bulma's core
  @import "~bulma/sass/utilities/_all";
  // Import Bulma and Buefy styles
  @import "~bulma";
  @import "~buefy/src/scss/buefy";
  // Import dark theme overrides
  @import "./components/utils/dark-theme.scss";

  html {
    background-color: #1a1a1a;
  }

  body {
    font-family: 'Open Sans', sans-serif;
    background-color: #1a1a1a;
    color: #e0e0e0;
  }

  #app {
    background-color: #1a1a1a;
    min-height: 100vh;
  }
</style>
