<template>
  <div class="pin-preview-modal" @mouseenter="showActions" @mouseleave="hideActions" @keydown="handleKeydown">
    <div class="pin-preview-image-container" @touchstart="handleTouchStart" @touchend="handleTouchEnd" @click="handleImageTap">
      <img :src="pinItem.large_image_url" alt="Image" class="pin-preview-image">
      <transition name="fade">
        <div v-if="(isMobile && mobileOverlayVisible) || (!isMobile && actionsVisible)" class="pin-preview-actions">
          <a :href="pinItem.referer || '#'" target="_blank" class="action-item" :class="{ 'action-item-disabled': !pinItem.referer }">
            <b-icon icon="web" custom-size="mdi-16px"></b-icon>
          </a>
          <a :href="pinItem.original_image_url || '#'" target="_blank" class="action-item" :class="{ 'action-item-disabled': !pinItem.original_image_url }">
            <b-icon icon="image" custom-size="mdi-16px"></b-icon>
          </a>
          <div class="action-item" @click="closeAndGoTo">
            <b-icon icon="link-variant" custom-size="mdi-16px"></b-icon>
          </div>
          <div
            v-if="similarPins.length > 0 && !similarSheetOpen"
            class="action-item"
            @click.stop="similarSheetOpen = true"
            title="Similar pins"
          >
            <b-icon icon="triangle" custom-size="mdi-16px"></b-icon>
          </div>
        </div>
      </transition>
      <transition name="fade">
        <div v-if="(isMobile && mobileOverlayVisible) || (!isMobile && metaVisible)" class="pin-preview-meta">
          <b-icon icon="account" custom-size="mdi-14px" class="user-icon"></b-icon>
          <span class="username">{{ pinItem.author }}</span>
          <template v-if="pinItem.tags.length > 0">
            <template v-for="tag in pinItem.tags">
              <span :key="tag" class="tag-text" @click.stop="goToTag(tag)">{{ tag }}</span>
            </template>
          </template>
        </div>
      </transition>
      <transition name="fade">
        <div v-if="((isMobile && mobileOverlayVisible) || (!isMobile && metaVisible)) && (pinItem.description || pinItem.referer)" class="pin-preview-description">
          <p v-if="pinItem.description" class="description" v-html="niceLinks(pinItem.description)"></p>
          <a v-if="pinItem.referer" :href="pinItem.referer" target="_blank" class="source-link">
            <b-icon icon="web" custom-size="mdi-14px"></b-icon>
          </a>
        </div>
      </transition>
      <transition name="fade">
        <div v-if="(isMobile && mobileOverlayVisible) || (!isMobile && actionsVisible)" class="pin-preview-navigation">
          <button
            v-if="canNavigatePrevious"
            class="nav-arrow nav-arrow-left"
            @click.stop.prevent="handleArrowClick(-1)"
            aria-label="Previous pin"
          >
            <b-icon icon="chevron-left" custom-size="mdi-24px"></b-icon>
          </button>
          <button
            v-if="canNavigateNext"
            class="nav-arrow nav-arrow-right"
            @click.stop.prevent="handleArrowClick(1)"
            aria-label="Next pin"
          >
            <b-icon icon="chevron-right" custom-size="mdi-24px"></b-icon>
          </button>
        </div>
      </transition>

      <transition name="sheet">
        <div v-if="similarSheetOpen" class="similar-sheet" @click.stop>
          <div v-if="selectedSimilarPin" class="similar-sheet-large">
            <img :src="selectedSimilarImageUrl" class="similar-sheet-large-img" />

            <!-- Tags -->
            <div v-if="selectedSimilarPin.tags && selectedSimilarPin.tags.length > 0" class="similar-sheet-meta">
              <template v-for="tag in selectedSimilarPin.tags">
                <span :key="tag" class="tag-text" @click.stop="goToTag(tag)">{{ tag }}</span>
              </template>
            </div>

            <!-- Nav arrows -->
            <button v-if="selectedSimilarIndex > 0" class="similar-nav-arrow similar-nav-left" @click.stop="navigateSimilar(-1)">
              <b-icon icon="chevron-left" custom-size="mdi-24px"></b-icon>
            </button>
            <button v-if="selectedSimilarIndex < similarPins.length - 1" class="similar-nav-arrow similar-nav-right" @click.stop="navigateSimilar(1)">
              <b-icon icon="chevron-right" custom-size="mdi-24px"></b-icon>
            </button>

            <!-- Actions + dismiss -->
            <div class="similar-sheet-actions">
              <a :href="selectedSimilarPin.referer || '#'" target="_blank" class="action-item" :class="{ 'action-item-disabled': !selectedSimilarPin.referer }">
                <b-icon icon="web" custom-size="mdi-16px"></b-icon>
              </a>
              <a :href="selectedSimilarPin.url || '#'" target="_blank" class="action-item" :class="{ 'action-item-disabled': !selectedSimilarPin.url }">
                <b-icon icon="image" custom-size="mdi-16px"></b-icon>
              </a>
              <div class="action-item" @click.stop="goToSelectedPin">
                <b-icon icon="link-variant" custom-size="mdi-16px"></b-icon>
              </div>
              <div class="action-item" @click.stop="similarSheetOpen = false" title="Close">
                <b-icon icon="triangle" custom-size="mdi-16px" class="sheet-close-icon"></b-icon>
              </div>
            </div>
          </div>

          <div class="similar-sheet-thumbs">
            <img
              v-for="pin in similarPins"
              :key="pin.id"
              :src="escapeUrl(pin.image.square.image)"
              :class="['similar-thumb', { selected: selectedSimilarPin && selectedSimilarPin.id === pin.id }]"
              @click.stop="selectedSimilarPin = pin"
            />
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import api from './api';
import pinHandler from './utils/PinHandler';
import niceLinks from './utils/niceLinks';

export default {
  name: 'PinPreview',
  props: ['pinItem', 'allPins', 'currentIndex'],
  data() {
    return {
      actionsVisible: false,
      metaVisible: false,
      actionsTimeout: null,
      metaTimeout: null,
      touchStartX: 0,
      touchEndX: 0,
      mobileOverlayVisible: false,
      isMobile: false,
      wasSwipe: false,
      similarPins: [],
      similarSheetOpen: false,
      selectedSimilarPin: null,
    };
  },
  computed: {
    canNavigatePrevious() {
      return this.allPins && this.currentIndex !== undefined && this.currentIndex > 0;
    },
    canNavigateNext() {
      return this.allPins && this.currentIndex !== undefined && this.currentIndex < this.allPins.length - 1;
    },
    selectedSimilarImageUrl() {
      if (!this.selectedSimilarPin) return '';
      const img = this.selectedSimilarPin.image;
      const src = img.standard ? img.standard.image : img.image;
      return pinHandler.escapeUrl(src);
    },
    selectedSimilarIndex() {
      if (!this.selectedSimilarPin) return -1;
      return this.similarPins.findIndex(p => p.id === this.selectedSimilarPin.id);
    },
  },
  watch: {
    pinItem: {
      immediate: true,
      handler() {
        this.similarSheetOpen = false;
        this.selectedSimilarPin = null;
        this.loadSimilarPins();
      },
    },
    similarSheetOpen(val) {
      if (val) {
        document.addEventListener('keydown', this.interceptEscape, true);
      } else {
        document.removeEventListener('keydown', this.interceptEscape, true);
      }
    },
  },
  mounted() {
    this.$el.focus();
    this.$el.setAttribute('tabindex', '0');
    this.checkMobile();
    window.addEventListener('resize', this.checkMobile);
  },
  beforeDestroy() {
    if (this.actionsTimeout) clearTimeout(this.actionsTimeout);
    if (this.metaTimeout) clearTimeout(this.metaTimeout);
    window.removeEventListener('resize', this.checkMobile);
    document.removeEventListener('keydown', this.interceptEscape, true);
  },
  methods: {
    interceptEscape(event) {
      if (event.key === 'Escape') {
        event.stopImmediatePropagation();
        this.similarSheetOpen = false;
      }
    },
    handleKeydown(event) {
      if (this.similarSheetOpen) {
        if (event.key === 'ArrowLeft') {
          event.preventDefault();
          this.navigateSimilar(-1);
        } else if (event.key === 'ArrowRight') {
          event.preventDefault();
          this.navigateSimilar(1);
        }
        return;
      }
      if (!this.allPins || this.allPins.length === 0) return;
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        this.navigatePin(-1);
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        this.navigatePin(1);
      }
    },
    navigatePin(direction) {
      if (!this.allPins || this.currentIndex === undefined) return;
      const newIndex = this.currentIndex + direction;
      if (newIndex >= 0 && newIndex < this.allPins.length) {
        this.$emit('navigate-pin', newIndex);
      }
    },
    handleArrowClick(direction, event) {
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.navigatePin(direction);
    },
    handleTouchStart(event) {
      this.touchStartX = event.touches[0].clientX;
    },
    handleTouchEnd(event) {
      this.touchEndX = event.changedTouches[0].clientX;
      this.handleSwipe();
    },
    handleSwipe() {
      const swipeThreshold = 50;
      const diff = this.touchStartX - this.touchEndX;
      if (Math.abs(diff) > swipeThreshold) {
        this.wasSwipe = true;
        if (diff > 0) {
          this.navigatePin(1);
        } else {
          this.navigatePin(-1);
        }
      } else {
        this.wasSwipe = false;
      }
    },
    showActions() {
      if (this.actionsTimeout) clearTimeout(this.actionsTimeout);
      if (this.metaTimeout) clearTimeout(this.metaTimeout);
      this.actionsVisible = true;
      this.metaVisible = true;
    },
    hideActions() {
      this.actionsTimeout = setTimeout(() => { this.actionsVisible = false; }, 500);
      this.metaTimeout = setTimeout(() => { this.metaVisible = false; }, 500);
    },
    closeAndGoTo() {
      if (this.$parent && this.$parent.close) this.$parent.close();
      this.$router.push({ name: 'pin', params: { pinId: this.pinItem.id } });
    },
    goToSelectedPin() {
      if (this.$parent && this.$parent.close) this.$parent.close();
      this.$router.push({ name: 'pin', params: { pinId: this.selectedSimilarPin.id } });
    },
    navigateSimilar(direction) {
      const next = this.selectedSimilarIndex + direction;
      if (next >= 0 && next < this.similarPins.length) {
        this.selectedSimilarPin = this.similarPins[next];
      }
    },
    goToTag(tag) {
      if (this.$parent && this.$parent.close) this.$parent.close();
      this.$router.push({ name: 'tag', params: { tag } });
    },
    escapeUrl: pinHandler.escapeUrl,
    loadSimilarPins() {
      this.similarPins = [];
      api.Pin.fetchSimilar(this.pinItem.id, 20).then((resp) => {
        this.similarPins = (resp.data.results || []).filter(p => p.image && p.image.square && p.image.square.image);
        this.selectedSimilarPin = this.similarPins.length > 0 ? this.similarPins[0] : null;
      }).catch(() => {});
    },
    niceLinks,
    checkMobile() {
      this.isMobile = window.innerWidth <= 768;
    },
    handleImageTap() {
      if (this.isMobile && !this.wasSwipe) {
        this.mobileOverlayVisible = !this.mobileOverlayVisible;
      }
      this.wasSwipe = false;
    },
  },
};
</script>

<style lang="scss" scoped>
@import './utils/fonts.scss';
@font-face {
  font-family: 'Rubik';
  src: url('../assets/Rubik/static/Rubik-Regular.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

.pin-preview-modal {
  outline: none;
  display: flex;
  flex-direction: column;
  max-width: 90vw;
  flex: 1;
  min-height: 0;
}

.pin-preview-image-container {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
  overflow: hidden;
}

.pin-preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  width: 100%;
  height: 100%;
}

.pin-preview-description {
  position: absolute;
  bottom: 12px;
  left: 8px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background-color: rgba(0, 0, 0, 0.8);
  border-radius: 999px;
  max-width: calc(100% - 16px);
  pointer-events: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 1);
  overflow: hidden;

  .description {
    font-family: 'Rubik', sans-serif;
    color: #ffffff;
    font-size: 0.725em;
    margin: 0;
    line-height: 1.4;
  }

  .source-link {
    display: flex;
    align-items: center;
    color: #ffffff;
    text-decoration: none;
    flex-shrink: 0;

    ::v-deep .mdi { color: #ffffff; }
    &:hover { opacity: 0.8; }
  }
}

.pin-preview-meta {
  position: absolute;
  top: 12px;
  left: 8px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 6px 12px;
  background-color: rgba(0, 0, 0, 0.8);
  border-radius: 999px;
  font-size: 0.725em;
  color: #ffffff;
  pointer-events: auto;
  max-width: calc(100% - 16px);
  overflow: hidden;

  .user-icon {
    flex-shrink: 0;
    margin-right: 2px;
    ::v-deep .mdi { color: #ffffff; }
  }

  .username {
    font-weight: bold;
    margin-right: 8px;
  }

  .tag-text {
    font-family: 'Rubik', sans-serif;
    background-color: #222222;
    border-radius: 100%;
    padding: 2px 8px;
    margin-left: 4px;
    cursor: pointer;

    &:first-of-type { margin-left: 0; }
    &:hover { background-color: #444444; }
  }
}

.pin-preview-actions {
  position: absolute;
  bottom: 12px;
  right: 8px;
  z-index: 10;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  padding: 4px;
  background-color: rgba(0, 0, 0, 0.8);
  border-radius: 999px;
  pointer-events: auto;

  .action-item {
    border-radius: 8px;
    padding: 6px;
    margin-left: 4px;
    background-color: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s ease;
    cursor: pointer;
    color: white;
    text-decoration: none;
    flex-shrink: 0;
    width: 28px;
    height: 28px;

    &:first-child { margin-left: 0; }
    &:hover { background-color: rgba(255, 255, 255, 0.1); }

    &.action-item-disabled {
      opacity: 0.5;
      cursor: not-allowed;
      pointer-events: none;
    }

    ::v-deep .mdi { color: white; }
  }
}

.pin-preview-navigation {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  z-index: 15;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  padding: 0 12px;

  .nav-arrow {
    pointer-events: auto;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: rgba(0, 0, 0, 0.8);
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.2s ease, transform 0.2s ease;
    color: white;
    outline: none;

    &:hover { background-color: rgba(0, 0, 0, 0.9); transform: scale(1.1); }
    &:active { transform: scale(0.95); }
    &:focus { outline: 2px solid rgba(255, 255, 255, 0.5); outline-offset: 2px; }

    ::v-deep .mdi { color: white; pointer-events: none; }
  }
}

/* Similar sheet */
.similar-sheet {
  position: absolute;
  inset: 0;
  z-index: 20;
  background: rgba(10, 10, 10, 0.98);
  display: flex;
  flex-direction: column;
  pointer-events: auto;
}

.similar-sheet-large {
  flex: 1;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 12px;
  min-height: 0;
}

.similar-sheet-large-img {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.similar-sheet-meta {
  position: absolute;
  top: 16px;
  left: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: calc(100% - 32px);
  pointer-events: auto;

  .tag-text {
    font-family: 'Rubik', sans-serif;
    font-size: 0.725em;
    background-color: rgba(0, 0, 0, 0.8);
    color: #ffffff;
    border-radius: 999px;
    padding: 2px 8px;
    cursor: pointer;

    &:hover { background-color: rgba(60, 60, 60, 0.9); }
  }
}

.similar-nav-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.8);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  outline: none;
  transition: background-color 0.2s ease;

  &:hover { background-color: rgba(0, 0, 0, 0.95); }
  ::v-deep .mdi { color: white; pointer-events: none; }
}

.similar-nav-left { left: 16px; }
.similar-nav-right { right: 16px; }

.similar-sheet-actions {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 4px;
  background-color: rgba(0, 0, 0, 0.8);
  border-radius: 999px;
  pointer-events: auto;

  .action-item {
    border-radius: 8px;
    padding: 6px;
    margin-left: 4px;
    background-color: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s ease;
    cursor: pointer;
    color: white;
    text-decoration: none;
    flex-shrink: 0;
    width: 28px;
    height: 28px;

    &:first-child { margin-left: 0; }
    &:hover { background-color: rgba(255, 255, 255, 0.1); }

    &.action-item-disabled {
      opacity: 0.5;
      cursor: not-allowed;
      pointer-events: none;
    }

    ::v-deep .mdi { color: white; }
  }

  .sheet-close-icon {
    transform: rotate(180deg);
  }
}

.similar-sheet-thumbs {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 3px;
  padding: 6px 8px 10px;
  flex-shrink: 0;
  justify-content: center;
}

.similar-thumb {
  flex: 1;
  max-width: 50px;
  min-width: 0;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  display: block;
  transition: opacity 0.15s ease;
  border: 2px solid transparent;

  &:hover { opacity: 0.8; }
  &.selected { border-color: #ffffff; opacity: 1; }
}

/* Transitions */
.sheet-enter-active, .sheet-leave-active {
  transition: transform 0.3s ease;
}

.sheet-enter, .sheet-leave-to {
  transform: translateY(100%);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
