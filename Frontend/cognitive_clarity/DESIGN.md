---
name: Cognitive Clarity
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#712ae2'
  on-secondary: '#ffffff'
  secondary-container: '#8a4cfc'
  on-secondary-container: '#fffbff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#191c1e'
  on-tertiary-container: '#818486'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#eaddff'
  secondary-fixed-dim: '#d2bbff'
  on-secondary-fixed: '#25005a'
  on-secondary-fixed-variant: '#5a00c6'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.2'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 24px
  margin: 32px
---

## Brand & Style
The design system is anchored in "Cognitive Clarity"—a philosophy that balances the raw power of artificial intelligence with the structured reliability of enterprise CRM software. The aesthetic is a fusion of **Modern Minimalism** and **Glassmorphism**, designed to evoke a sense of high-fidelity precision and forward-thinking efficiency.

The target audience consists of high-performing sales professionals and executive networking teams who require tools that feel as premium as the services they provide. The emotional response is one of calm confidence; the UI recedes into the background, allowing data to take center stage, while subtle light-refraction effects and translucent layers signal the "intelligent" layer of processing happening beneath the surface.

## Colors
The palette is centered around "Intelligence Blue," a deep, authoritative navy that provides a stable foundation for enterprise data. This is contrasted by "AI Purple," a vibrant, electric violet used exclusively for high-value interactions, AI processing states, and primary calls to action.

In both light and dark modes, the system maintains high contrast for legibility. 
- **Primary (Intelligence Blue):** Used for sidebars, primary text, and core branding.
- **Accent (AI Purple):** Denotes the "magic" of the AI—scanning animations, insight highlights, and new lead notifications.
- **Grays:** A neutral scale ranging from slate to cool silver is used for borders, secondary text, and inactive states to ensure the interface feels airy and organized.

## Typography
This design system utilizes **Geist** for its technical precision and modern, monolinear construction. The typographic hierarchy is designed for high-density data views, prioritizing clarity in scanning business card details and CRM lists.

- **Scale:** Bold, tight tracking is used for large headlines to emphasize a premium feel. 
- **Body:** Standard body text is set with generous line heights to prevent fatigue during long periods of data entry or lead review.
- **Labels:** Small caps or medium-weight labels are used for metadata (e.g., "Company Size," "Last Contacted") to differentiate them clearly from user-generated content.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a strict 8px baseline. The standard desktop view utilizes a 12-column grid with 24px gutters.

- **Margins:** Outer page margins are 32px on desktop, scaling down to 16px on mobile.
- **Vertical Spacing:** Modules and cards are separated by "lg" (40px) or "xl" (64px) units to create "purposeful whitespace," ensuring the high-density data does not feel cluttered.
- **Mobile Reflow:** On mobile, the 12-column grid collapses to a single column. Cards occupy the full width of the screen minus the side margins, and navigation moves to a bottom-fixed glass bar.

## Elevation & Depth
Depth is communicated through **Glassmorphism** and **Ambient Shadows**. This design system avoids heavy drop shadows in favor of light-diffusing layers that feel like stacked panes of glass.

1.  **The Base Layer:** Solid background (Light or Dark).
2.  **The Container Layer:** Semi-transparent "glass" surfaces (70% opacity in light mode, 60% in dark mode) with a `20px` backdrop blur.
3.  **Borders:** Every glass element features a "subtle border"—a 1px inner stroke that is slightly lighter than the background to simulate a glass edge.
4.  **Shadows:** Low-opacity, extra-diffused shadows (`blur: 30px, opacity: 5%`) are used only for the highest level elements, such as modals or active "Floating Action Buttons" for the camera scanner.

## Shapes
The shape language is sophisticated and "Soft-Industrial." Standard containers like cards and input fields use an **8px (0.5rem) radius**. Larger layout sections, such as the main dashboard content area, use a **16px (1rem) radius**.

This roundedness provides a friendly, approachable counterpoint to the sharp, technical Geist typeface. Interaction states (like hovering over a lead card) may subtly increase the perceived depth or "squish" of the radius to provide tactile feedback.

## Components
Consistent implementation of components is vital for the premium feel of the design system.

- **Buttons:** Primary buttons use a gradient of AI Purple with a soft glow shadow. Secondary buttons are "ghost" style with a 1px border. All buttons feature an 8px radius.
- **Glass Cards:** The primary vessel for business card data. They must include a `backdrop-filter: blur(20px)` and a subtle 1px border.
- **Scanning HUD:** A specialized component for the business card scanner that uses a neon-purple tracking frame and translucent overlays to highlight detected text in real-time.
- **Input Fields:** Minimalist design with a bottom-only border that transitions to a full 1px outline in AI Purple upon focus.
- **Chips:** Small, highly rounded (pill-shaped) tags used for contact status (e.g., "New," "In-Progress," "Converted"), utilizing low-saturation background tints to prevent visual noise.
- **AI Insight Banners:** Subtle, top-aligned banners with a blurred purple background used to suggest "Next Best Actions" for a specific lead.