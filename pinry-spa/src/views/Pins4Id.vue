<template>
  <div>
    <PHeader></PHeader>

    <div v-if="pin" class="permalink-wrap">
      <!-- URL header -->
      <div v-if="sourceUrl" class="pin-meta-row">
        <div class="pin-url-pill" @click="copyUrl" :title="sourceUrl">
          <span class="pin-url-text">{{ sourceUrl }}</span>
          <b-icon :icon="copied ? 'check' : 'content-copy'" custom-size="mdi-14px" class="copy-icon"></b-icon>
        </div>
      </div>

      <!-- Large image -->
      <div class="permalink-image-wrap">
        <img :src="pinImageUrl" :alt="pin.description" class="permalink-image" />
      </div>

      <!-- Tags -->
      <div v-if="pin.tags && pin.tags.length" class="pin-tags-row">
        <router-link
          v-for="tag in pin.tags"
          :key="tag"
          :to="`/search/?tags=${encodeURIComponent(tag)}`"
          class="pin-tag-pill"
        >{{ tag }}</router-link>
      </div>
    </div>

    <!-- Similar pins gallery -->
    <Pins v-if="pinId" :pin-filters="similarFilter"></Pins>
  </div>
</template>

<script>
import API from '../components/api';
import pinHandler from '../components/utils/PinHandler';
import PHeader from '../components/PHeader.vue';
import Pins from '../components/Pins.vue';

export default {
  name: 'Pins4Id',
  components: { PHeader, Pins },
  data() {
    return {
      pin: null,
      pinId: null,
      similarFilter: { similarToPin: null },
      copied: false,
    };
  },
  computed: {
    pinImageUrl() {
      if (!this.pin || !this.pin.image) return null;
      return pinHandler.escapeUrl(this.pin.image.image);
    },
    sourceUrl() {
      if (!this.pin) return null;
      return this.pin.referer || this.pin.url || null;
    },
  },
  created() {
    this.initialize();
  },
  beforeRouteUpdate(to, from, next) {
    this.pinId = to.params.pinId;
    this.similarFilter = { similarToPin: to.params.pinId };
    this.loadPin(to.params.pinId);
    next();
  },
  methods: {
    initialize() {
      const { pinId } = this.$route.params;
      this.pinId = pinId;
      this.similarFilter = { similarToPin: pinId };
      this.loadPin(pinId);
    },
    loadPin(pinId) {
      this.pin = null;
      API.fetchPin(pinId).then((resp) => {
        const [pin] = resp.data.results;
        this.pin = pin;
      }).catch(() => {});
    },
    copyUrl() {
      if (!this.sourceUrl) return;
      navigator.clipboard.writeText(this.sourceUrl).then(() => {
        this.copied = true;
        setTimeout(() => { this.copied = false; }, 2000);
      });
    },
  },
};
</script>

<style scoped lang="scss">
@font-face {
  font-family: 'Rubik';
  src: url('../assets/Rubik/static/Rubik-Regular.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

.permalink-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px 16px 0;
}

.pin-meta-row {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
  width: 100%;
}

.pin-url-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: #000002;
  border-radius: 999px;
  padding: 3px 10px 3px 14px;
  font-family: 'Rubik', sans-serif;
  font-size: 0.725em;
  font-weight: bold;
  color: #fefefe;
  cursor: pointer;
  max-width: min(100%, 600px);
  transition: background-color 0.15s ease;

  &:hover { background-color: #1a1a1a; }
}

.pin-url-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #fefefe;
}

.copy-icon {
  flex-shrink: 0;
  ::v-deep .mdi { color: #fefefe; }
}

.permalink-image-wrap {
  width: 100%;
  max-width: 800px;
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.permalink-image {
  max-width: 100%;
  border-radius: 12px;
  display: block;
}

.pin-tags-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin-bottom: 24px;
  max-width: 800px;
  width: 100%;
}

.pin-tag-pill {
  display: inline-flex;
  align-items: center;
  background-color: #000002;
  border-radius: 999px;
  padding: 3px 14px;
  font-family: 'Rubik', sans-serif;
  font-size: 0.725em;
  font-weight: bold;
  color: #fefefe !important;
  text-decoration: none;
  transition: background-color 0.15s ease;

  &:hover { background-color: #1a1a1a; }
}
</style>
