<template>
  <div class="p-header">
    <!-- Placeholder hitbox for logo area -->
    <div
      class="logo-placeholder"
      @mouseenter="showLogoOnHover"
      @mouseleave="handleLogoPlaceholderLeave"
      @click="handlePlaceholderClick"
    >
      <transition name="fade">
        <div
          v-if="!logoHidden"
          class="nav-icon-container"
          @click="toggleMenu"
          @mouseenter="showMenuOnHover"
          @mouseleave="handleMouseLeave"
        >
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
              v-if="user.loggedIn"
              class="nav-menu-item"
              @click="handleProfileClick"
            >
              Profile
            </div>
            <div
              v-if="!user.loggedIn && signUpAllowed"
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
      </transition>
    </div>
    <!-- FAB Add Pin Button -->
    <div
      v-if="user.loggedIn"
      class="fab-add-pin"
      :class="{ 'fade-out': iconHidden }"
      @click.stop="handleFabClick"
    >
      <img
        :src="iconSrc"
        alt="Add Pin"
        class="fab-icon"
        :class="{ 'is-spinning': fabSpinning }"
      />
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
      iconHidden: false,
      logoHidden: false,
      iconFadeTimeout: null,
      iconShowTimeout: null,
      logoFadeTimeout: null,
      fabSpinning: false,
      logoPlaceholderHovered: false,
      hoverMenuTimeout: null,
      user: {
        loggedIn: false,
        meta: {},
      },
      signUpAllowed: false,
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
        // Restart logo fade timeout when menu closes
        if (this.logoFadeTimeout) {
          clearTimeout(this.logoFadeTimeout);
        }
        this.logoFadeTimeout = setTimeout(() => {
          this.logoHidden = true;
        }, 3000);
      } else {
        // Clear logo fade timeout when menu opens
        if (this.logoFadeTimeout) {
          clearTimeout(this.logoFadeTimeout);
        }
        this.logoHidden = false;
      }
    },
    handleMouseLeave() {
      // Close menu on mouse leave from icon container with delay
      if (!this.menuHovered) {
        this.dismissTimeout = setTimeout(() => {
          this.menuOpen = false;
        }, 1500);
      }
    },
    handleMenuLeave() {
      this.menuHovered = false;
      this.dismissTimeout = setTimeout(() => {
        this.menuOpen = false;
      }, 1500);
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
    handleFabClick() {
      this.fabSpinning = true;
      setTimeout(() => {
        this.fabSpinning = false;
        this.createPin();
      }, 400);
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
    handleScroll() {
      // === FAB behavior: hide on scroll, show 500ms after scroll stops ===
      // Clear show timeout if scrolling again
      if (this.iconShowTimeout) {
        clearTimeout(this.iconShowTimeout);
        this.iconShowTimeout = null;
      }
      // Hide FAB immediately on scroll start
      if (!this.iconHidden) {
        this.iconHidden = true;
      }
      // Show FAB 500ms after scroll stops
      this.iconShowTimeout = setTimeout(() => {
        this.iconHidden = false;
      }, 500);

      // === Logo behavior: show on scroll, hide 3s after scroll stops ===
      this.logoHidden = false;
      if (this.logoFadeTimeout) {
        clearTimeout(this.logoFadeTimeout);
      }
      this.logoFadeTimeout = setTimeout(() => {
        if (!this.menuOpen) {
          this.logoHidden = true;
        }
      }, 3000);
    },
    showLogoOnHover() {
      this.logoPlaceholderHovered = true;
      this.logoHidden = false;
      // Clear any pending dismiss timeout
      if (this.dismissTimeout) {
        clearTimeout(this.dismissTimeout);
        this.dismissTimeout = null;
      }
      // Clear any pending fade timeout
      if (this.logoFadeTimeout) {
        clearTimeout(this.logoFadeTimeout);
        this.logoFadeTimeout = null;
      }
      // Show menu on hover after a short delay
      if (!this.menuOpen) {
        this.hoverMenuTimeout = setTimeout(() => {
          if (this.logoPlaceholderHovered && !this.menuOpen) {
            this.menuOpen = true;
          }
        }, 300);
      }
    },
    showMenuOnHover() {
      // Clear any pending dismiss timeout
      if (this.dismissTimeout) {
        clearTimeout(this.dismissTimeout);
        this.dismissTimeout = null;
      }
      // Show menu on hover after a short delay
      if (!this.menuOpen) {
        if (this.hoverMenuTimeout) {
          clearTimeout(this.hoverMenuTimeout);
        }
        this.hoverMenuTimeout = setTimeout(() => {
          if (!this.menuOpen) {
            this.menuOpen = true;
          }
        }, 300);
      }
    },
    handleLogoPlaceholderLeave() {
      this.logoPlaceholderHovered = false;
      // Clear hover menu timeout
      if (this.hoverMenuTimeout) {
        clearTimeout(this.hoverMenuTimeout);
        this.hoverMenuTimeout = null;
      }
      // Only hide logo if menu is not open
      if (!this.menuOpen) {
        if (this.logoFadeTimeout) {
          clearTimeout(this.logoFadeTimeout);
        }
        this.logoFadeTimeout = setTimeout(() => {
          if (!this.menuOpen && !this.logoPlaceholderHovered) {
            this.logoHidden = true;
          }
        }, 3000);
      }
    },
    handlePlaceholderClick() {
      // If logo is hidden, show it and toggle menu
      if (this.logoHidden) {
        this.logoHidden = false;
        this.$nextTick(() => {
          this.toggleMenu();
        });
      }
    },
  },
  beforeMount() {
    this.initializeUser();
    api.Site.fetchSettings().then((resp) => {
      this.signUpAllowed = resp.data.allow_new_registrations;
    });
    // Close menu when clicking outside
    document.addEventListener('click', this.handleClickOutside);
    // Listen for scroll to show/hide icon
    window.addEventListener('scroll', this.handleScroll);
    // Hide logo after 3s on initial load
    this.logoFadeTimeout = setTimeout(() => {
      this.logoHidden = true;
    }, 3000);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleClickOutside);
    window.removeEventListener('scroll', this.handleScroll);
    if (this.dismissTimeout) {
      clearTimeout(this.dismissTimeout);
    }
    if (this.iconFadeTimeout) {
      clearTimeout(this.iconFadeTimeout);
    }
    if (this.iconShowTimeout) {
      clearTimeout(this.iconShowTimeout);
    }
    if (this.logoFadeTimeout) {
      clearTimeout(this.logoFadeTimeout);
    }
    if (this.hoverMenuTimeout) {
      clearTimeout(this.hoverMenuTimeout);
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
  z-index: 30;
}

.logo-placeholder {
  position: fixed;
  top: 20px;
  left: 20px;
  width: 48px;
  height: 48px;
  z-index: 1000;
  cursor: pointer;
}

.nav-icon-container {
  position: relative;
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

// Fade transition for logo and FAB
.fade-enter-active {
  transition: opacity 0.3s ease;
}

.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter {
  opacity: 0;
}

.fade-leave-to {
  opacity: 0;
}

// FAB Add Pin Button
.fab-add-pin {
  position: fixed;
  bottom: 36px;
  right: 36px;
  width: 64px;
  height: 64px;
  background-color: #ff42ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 20;
  box-shadow: 0 4px 12px rgba(255, 66, 255, 0.4);
  transition: background-color 0.2s ease, opacity 0.3s ease;
  opacity: 1;

  &.fade-out {
    opacity: 0;
    pointer-events: none;
  }

  &:hover {
    background-color: #ff66ff;

    .fab-icon {
      transform: scaleX(-1) rotate(45deg);
    }
  }
}

.fab-icon {
  width: 48px;
  height: 48px;
  transform: scaleX(-1);
  filter: grayscale(1) brightness(0.25);
  transition: transform 0.2s ease;

  &.is-spinning {
    animation: spinAccel 0.4s cubic-bezier(0.2, 0, 1, 1) forwards;
  }
}

@keyframes spinAccel {
  0% {
    transform: scaleX(-1) rotate(0deg);
  }
  100% {
    transform: scaleX(-1) rotate(720deg);
  }
}
</style>
