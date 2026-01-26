<template>
  <div class="p-header">
    <div class="nav-icon-container" @click="toggleMenu" @mouseleave="handleMouseLeave">
      <img
        :src="iconSrc"
        alt="Menu"
        class="nav-icon"
        :class="{ 'is-open': menuOpen }"
      />
      <transition name="menu">
        <div v-if="menuOpen" class="nav-menu" @mouseenter="keepMenuOpen" @mouseleave="handleMenuLeave">
          <div
            class="nav-menu-item"
            @click="handlePinsClick"
          >
            Pins
          </div>
          <div
            v-if="user.loggedIn"
            class="nav-menu-item"
            @click="handleAddClick"
          >
            Add
          </div>
          <div
            class="nav-menu-item"
            @click="handleSearchClick"
          >
            Search
          </div>
          <div
            v-if="user.loggedIn"
            class="nav-menu-item"
            @click="handleProfileClick"
          >
            Profile
          </div>
          <div
            v-if="!user.loggedIn"
            class="nav-menu-item"
            @click="handleSignUpClick"
          >
            Sign Up
          </div>
          <div
            v-if="!user.loggedIn"
            class="nav-menu-item"
            @click="handleLogInClick"
          >
            Log In
          </div>
          <div
            v-if="user.loggedIn"
            class="nav-menu-item"
            @click="handleLogOutClick"
          >
            Log Out
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import api from './api';
import modals from './modals';
import pinstleLogo from '../assets/pinstle-logo.png';

export default {
  name: 'p-header',
  data() {
    return {
      menuOpen: false,
      menuHovered: false,
      dismissTimeout: null,
      user: {
        loggedIn: false,
        meta: {},
      },
    };
  },
  computed: {
    iconSrc() {
      return pinstleLogo;
    },
  },
  methods: {
    handleClickOutside(event) {
      const container = this.$el.querySelector('.nav-icon-container');
      if (container && !container.contains(event.target)) {
        this.menuOpen = false;
        this.menuHovered = false;
      }
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen;
      if (!this.menuOpen) {
        this.menuHovered = false;
      }
    },
    handleMouseLeave() {
      // Close menu on mouse leave from icon container with delay
      if (!this.menuHovered) {
        this.dismissTimeout = setTimeout(() => {
          this.menuOpen = false;
        }, 700);
      }
    },
    handleMenuLeave() {
      this.menuHovered = false;
      this.dismissTimeout = setTimeout(() => {
        this.menuOpen = false;
      }, 700);
    },
    keepMenuOpen() {
      this.menuHovered = true;
      // Clear any pending dismiss timeout
      if (this.dismissTimeout) {
        clearTimeout(this.dismissTimeout);
        this.dismissTimeout = null;
      }
    },
    handlePinsClick() {
      this.$router.push({ name: 'home' });
      this.menuOpen = false;
    },
    handleAddClick() {
      this.createPin();
      this.menuOpen = false;
    },
    handleSearchClick() {
      this.$router.push({ name: 'search' });
      this.menuOpen = false;
    },
    handleProfileClick() {
      if (this.user.loggedIn && this.user.meta.username) {
        this.$router.push({
          name: 'profile4user',
          params: { username: this.user.meta.username },
        });
        this.menuOpen = false;
      }
    },
    handleSignUpClick() {
      this.signUp();
      this.menuOpen = false;
    },
    handleLogInClick() {
      this.logIn();
      this.menuOpen = false;
    },
    handleLogOutClick() {
      this.logOut();
      this.menuOpen = false;
    },
    onLoginSucceed() {
      this.initializeUser(true);
    },
    onSignUpSucceed() {
      this.initializeUser(true);
    },
    logOut() {
      api.User.logOut().then(
        () => {
          window.location.reload();
        },
      );
    },
    logIn() {
      modals.openLogin(this, this.onLoginSucceed);
    },
    createPin() {
      modals.openPinEdit(
        this,
        { username: this.user.meta.username },
      );
    },
    createBoard() {
      modals.openBoardCreate(this);
    },
    signUp() {
      modals.openSignUp(this, this.onSignUpSucceed);
    },
    initializeUser(force = false) {
      const self = this;
      api.User.fetchUserInfo(force).then(
        (user) => {
          if (user === null) {
            self.user.loggedIn = false;
            self.user.meta = {};
          } else {
            self.user.meta = user;
            self.user.loggedIn = true;
          }
        },
      );
    },
  },
  beforeMount() {
    this.initializeUser();
    // Close menu when clicking outside
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleClickOutside);
    if (this.dismissTimeout) {
      clearTimeout(this.dismissTimeout);
    }
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

.p-header {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.nav-icon-container {
  position: fixed;
  top: 20px;
  left: 20px;
  cursor: pointer;
  z-index: 1001;
}

.nav-icon {
  width: 48px;
  height: 48px;
  transition: filter 0.3s ease;

  // When menu is open, show white
  &.is-open {
    filter: brightness(0) invert(1);
  }

  // When menu is closed, show natural colors (no filter)
  &:not(.is-open) {
    filter: none;
  }
}

.nav-menu {
  position: absolute;
  top: 60px;
  left: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: fit-content;
}

.nav-menu-item {
  background-color: #000002;
  color: #fefefe;
  padding: 6px 12px;
  border-radius: 999px;
  font-family: 'Rubik', sans-serif;
  font-size: 0.725em;
  font-weight: bold;
  white-space: nowrap;
  cursor: pointer;
  transition: background-color 0.2s ease;
  user-select: none;

  &:hover {
    background-color: #0a0a0a;
  }
}

// Menu animation
.menu-enter-active {
  animation: slideDownFadeIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.menu-leave-active {
  animation: slideUpFadeOut 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes slideDownFadeIn {
  0% {
    opacity: 0;
    transform: translateY(-20px) scale(0.9);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes slideUpFadeOut {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-20px) scale(0.9);
  }
}
</style>
