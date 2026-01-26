# UI Documentation

## Overview

This document tracks UI changes, design decisions, and component notes for the Pinry project.

## Theme

### Dark Theme
- The application uses a dark theme by default
- Main background: `#1a1a1a`
- Surface colors: `#2d2d2d` (primary), `#3a3a3a` (elevated)
- Text colors: `#e0e0e0` (primary), `#a0a0a0` (secondary)
- Border color: `#404040`
- Link color: `#4a9eff`

### Theme Files
- `pinry-spa/src/components/utils/dark-theme.scss` - Main dark theme overrides

## Components

### Navigation
- **PHeader.vue** - Main navigation header
  - Removed: Bookmarklet link, Browser extensions dropdown, Language dropdown
  - Contains: Create dropdown, My dropdown (when logged in), Search, Auth buttons

### Images & Assets
- **Location**: `pinry-spa/src/assets/`
  - `logo-dark.png` - Dark theme logo
  - `logo-light.png` - Light theme logo (not currently used)
  - `loader.gif` - Loading spinner
  - `pinry-placeholder.jpg` - Placeholder image

### Avatars
- Gravatar has been removed
- Using SVG placeholder avatars (base64 encoded)
- Placeholder matches dark theme colors

## Removed Features

- Bookmarklet functionality
- Browser extensions links
- Language switcher dropdown
- Gravatar integration

## Tech Stack

- **Vue.js 2.6.10** - Frontend framework
- **Bulma 0.7.5** - CSS framework
- **Buefy 0.8.20** - Vue component library
- **SCSS** - Styling preprocessor
- **Vue Router** - Routing
- **Vue I18n** - Internationalization

## Simplification

- Remove existing navigation completely
- Replace with a single icon in the upper left.
- Icon should float and be fixed
- use pinry-spa/src/assets/pinstle-logo.png
- When clicking this icon, the following items appear below it in a list
-- Pins (back to home)
-- Add (opens the add pin dialogue)
-- Search 
-- Profile
-- Each of these subitems will be enclosed in a container with 100% rounded corners
-- 10px padding all around
-- container is not fixed width but stretches to contents
-- The sub mentu items animate down from the main icon... quickly with a nice curve on them. they should also fade in quickly
-- container has #000002 background with almost pure white text .25em
-- onmouseover the background gets subtly lighter
- on mouseout or click/tap of icon again the submenu is hidden using reverse of this animation. main icon returns to native pink color
- Use Rubik font (in assets)

- Pin containers should not show the username that pinned... just the image only
- pin container should have rounded corners (8px radius)
-- Actions
- the actions (save to board, delete, edit) should be 33% smaller 
- should also have rounded corners
- 4px padding between items. should not have margin between. enclose in a single black rounded corner (100%) container if necessary. 
- fixed in the lower right (same margin from edge of image though) - boost it up 4 px from bottom
- should fade in/out quickly 

