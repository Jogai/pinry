<template>
    <div class="user-profile-card">
      <div id="user-home-container">
        <div class="profile-card">
          <div class="profile-card-header">
            <figure class="avatar-figure">
              <b-skeleton width="64px" height="64px" :active="avatarLoading" circle></b-skeleton>
              <img
                @load="onAvatarLoaded"
                v-show="!avatarLoading"
                :src="user.avatar"
                alt="avatar"
                class="avatar-img"
              >
            </figure>
            <div class="profile-identity" v-show="!avatarLoading">
              <p class="profile-username">{{ user.username }}</p>
              <p class="profile-location">@{{ location }}</p>
            </div>
          </div>

          <nav class="profile-tabs">
            <button
              class="tab-btn"
              :class="{ 'is-active': inPins }"
              @click="go2UserPins"
            >
              <b-icon type="is-light" icon="image" custom-size="mdi-16px"></b-icon>
              <span>{{ $t("pinsUserProfileCardLink") }}</span>
            </button>
            <button
              class="tab-btn"
              :class="{ 'is-active': inBoard }"
              @click="go2UserBoard"
            >
              <b-icon type="is-light" icon="folder-multiple-image" custom-size="mdi-16px"></b-icon>
              <span>{{ $t("boardsUserProfileCardLink") }}</span>
            </button>
            <button
              class="tab-btn"
              :class="{ 'is-active': inProfile }"
              @click="go2UserProfile"
            >
              <b-icon type="is-light" icon="account" custom-size="mdi-16px"></b-icon>
              <span>{{ $t("profileUserProfileCardLink") }}</span>
            </button>
          </nav>
        </div>
      </div>
    </div>
</template>

<script>
import api from './api';

export default {
  name: 'UserProfileCard.vue',
  props: {
    username: String,
    inBoard: {
      type: Boolean,
      default: false,
    },
    inPins: {
      type: Boolean,
      default: false,
    },
    inProfile: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      location: window.location.host,
      avatarLoading: true,
      user: {
        avatar: '',
        username: '',
      },
    };
  },
  beforeMount() {
    this.initializeUser(this.username);
  },
  methods: {
    go2UserBoard() {
      this.$router.push(
        { name: 'boards4user', params: { username: this.username } },
      );
    },
    go2UserProfile() {
      this.$router.push(
        { name: 'profile4user', params: { username: this.username } },
      );
    },
    go2UserPins() {
      this.$router.push(
        { name: 'user', params: { user: this.username } },
      );
    },
    onAvatarLoaded() {
      this.avatarLoading = false;
    },
    initializeUser(username) {
      const self = this;
      api.User.fetchUserInfoByName(username).then(
        (user) => {
          if (user === null) {
            self.$router.push(
              { name: 'PageNotFound' },
            );
          } else {
            self.user.avatar = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMmQyZDJkIi8+CjxwYXRoIGQ9Ik0yNCAyNEMyNy4zMTM3IDI0IDMwIDIxLjMxMzcgMzAgMThDMzAgMTQuNjg2MyAyNy4zMTM3IDEyIDI0IDEyQzIwLjY4NjMgMTIgMTggMTQuNjg2MyAxOCAxOEMxOCAyMS4zMTM3IDIwLjY4NjMgMjQgMjQgMjRaIiBmaWxsPSIjNjY2NjY2Ii8+CjxwYXRoIGQ9Ik0yNCAyNkMyMC42ODYzIDI2IDE3LjI2MzcgMjcuMjEwNSAxNC42OTMgMjkuMDkzOEMxMi4xMjIzIDMwLjk3NyAxMC41IDMzLjQyOTMgMTAuNSAzNlY0MEgzNy41VjM2QzM3LjUgMzMuNDI5MyAzNS44Nzc3IDMwLjk3NyAzMy4zMDcgMjkuMDkzOEMzMC43MzYzIDI3LjIxMDUgMjcuMzEzNyAyNiAyNCAyNloiIGZpbGw9IiM2NjY2NjYiLz4KPC9zdmc+';
            self.user.username = user.username;
            self.user.meta = user;
          }
        },
      );
    },
  },
};
</script>

<style lang="scss" scoped>
@font-face {
  font-family: 'Rubik';
  src: url('../assets/Rubik/static/Rubik-Regular.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}

#user-home-container {
  margin-top: 2rem;
  margin-left: auto;
  margin-right: auto;
}

@import './utils/grid-layout';
@include screen-grid-layout("#user-home-container");

.profile-card {
  background-color: #2d2d2d;
  border-radius: 8px;
  overflow: hidden;
}

.profile-card-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.75rem 1.75rem 1.25rem;
}

.avatar-figure {
  flex-shrink: 0;
  margin: 0;
  width: 64px;
  height: 64px;
}

.avatar-img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.profile-identity {
  min-width: 0;
}

.profile-username {
  font-family: 'Rubik', sans-serif;
  font-size: 1.4rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 2px;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-location {
  font-size: 0.8rem;
  color: #888888;
  margin: 0;
}

.profile-tabs {
  display: flex;
  flex-direction: row;
  gap: 6px;
  padding: 0 1.75rem 1.5rem;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 999px;
  border: 1px solid #404040;
  background-color: transparent;
  color: #e0e0e0;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;

  ::v-deep .mdi { color: #e0e0e0; transition: color 0.15s ease; }

  &:hover {
    background-color: #3a3a3a;
    border-color: #555555;
  }

  &.is-active {
    background-color: #ff42ff;
    border-color: #ff42ff;
    color: #ffffff;

    ::v-deep .mdi { color: #ffffff; }
  }
}
</style>
