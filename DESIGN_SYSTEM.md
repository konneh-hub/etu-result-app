# Design System Documentation

## Visual Design Overview

The ETU Results Management System uses a modern, professional design system with a purple gradient theme, clean typography, and intuitive navigation.

## Color Palette

### Primary Colors
- **Brand Blue**: `#0d6efd`
  - Primary buttons and highlights
  - Navigation active states
  - Primary badges

- **Success Green**: `#198754`
  - Positive metrics (GPA, courses)
  - Completion indicators
  - Success badges

- **Info Cyan**: `#0dcaf0`
  - Information cards
  - Secondary highlights
  - Info badges

- **Warning Yellow**: `#ffc107`
  - Alert indicators
  - Warning messages
  - Attention-needed cards

- **Danger Red**: `#dc3545`
  - Critical actions
  - Error states
  - Danger alerts

### Neutral Colors
- **Dark**: `#212529` - Text and borders
- **Muted**: `#6c757d` - Secondary text
- **Light**: `#f8f9fa` - Backgrounds
- **White**: `#ffffff` - Card backgrounds

### Gradient Backgrounds
- **Login Gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- **Navbar Gradient**: `linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)`
- **Sidebar Gradient**: `linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)`
- **Profile Gradient**: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

## Typography

### Font Family
```css
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

### Font Sizes
- **H1** (Page Headers): `1.8rem` - Bold (700)
- **H2** (Section Headers): `1.5rem` - Bold (700)
- **H3** (Subsections): `1.25rem` - Semi-bold (600)
- **H4** (Card Headers): `1rem` - Semi-bold (600)
- **H5** (Mini Headers): `0.95rem` - Semi-bold (600)
- **Body**: `1rem` - Regular (400)
- **Small**: `0.9rem` - Regular (400)
- **Tiny**: `0.85rem` - Regular (400)

### Font Weights
- **400**: Regular body text, descriptions
- **500**: Medium emphasis, badges
- **600**: Semi-bold for subheadings, labels
- **700**: Bold for main headings and CTAs

## Spacing System

### Base Unit: 0.5rem (8px)

```
Margin/Padding Scale:
- xs: 0.25rem  (4px)
- sm: 0.5rem   (8px)
- md: 1rem     (16px)
- lg: 1.5rem   (24px)
- xl: 2rem     (32px)
- 2xl: 3rem    (48px)
```

### Usage
- Card padding: `1.5-2rem` (24-32px)
- Section margins: `1.5-2rem` (24-32px)
- Component spacing: `0.75-1rem` (12-16px)
- Table cell padding: `0.75-1rem` (12-16px)

## Layout System

### Container
- Max width: None (full width - responsive)
- Breakpoints:
  - Mobile: 0-767px
  - Tablet: 768px-1023px
  - Desktop: 1024px+

### Grid System (Bootstrap 5)
- 12 column grid
- Gap: `1.5rem` (24px)
- Responsive classes: xs, sm, md, lg, xl

### Sidebar
- Width: `250px` (fixed)
- Min-height: `100vh`
- Position: Sticky
- Hides at: 768px breakpoint

### Main Content
- Padding: `2rem`
- Responsive: `1rem` on mobile

## Component Design

### Cards (Dashboard-card)
```css
background: #fff;
border-radius: 0.75rem;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
border-top: 4px solid [color];
padding: 1.5rem;
transition: all 0.3s ease;

:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
```

### Statistics Cards
- **Height**: Adaptive (min 150px)
- **Layout**: Flex (space-between)
- **Text Colors**: 
  - Number: Brand color
  - Label: Muted gray

### Tables
```css
background: #fff;
border-radius: 0.75rem;
overflow: hidden;

thead {
  background-color: #f8f9fa;
  text-transform: uppercase;
  font-size: 0.85rem;
}

tbody tr:hover {
  background-color: #f8f9fa;
}
```

### Buttons
```css
border-radius: 0.5rem;
padding: 0.5rem 1.2rem;
font-weight: 600;
border: none;
transition: all 0.3s ease;

:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-sm {
  padding: 0.35rem 0.8rem;
  font-size: 0.85rem;
}
```

### Badges
```css
padding: 0.4rem 0.8rem;
font-weight: 600;
font-size: 0.85rem;
letter-spacing: 0.3px;
border-radius: 0.25rem;
```

### Forms
```css
.form-control {
  border: 2px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.15);
}
```

### Info Box
```css
background: #fff;
border-left: 4px solid [color];
padding: 1.5rem;
border-radius: 0.5rem;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
```

## Navigation

### Navbar
- Height: Auto
- Sticky: top
- Gradient background
- Responsive hamburger at 768px

### Sidebar
- Dark gradient background
- Rounded navigation links
- Active state highlight
- Icon support with Font Awesome
- Sticky positioning

### Breadcrumbs
- Transparent background
- Links: Primary color
- Active: Primary bold

## Animations & Transitions

### Timing
- Quick: `0.2s`
- Standard: `0.3s` (default)
- Slow: `0.5s`
- Easing: `ease` / `ease-in-out`

### Effects
- **Hover**: `translateY(-2px) / translateY(-4px)`
- **Focus**: Color change + shadow
- **Active**: `translateY(0)`
- **Fade**: Opacity transition

### Keyframe Animations
- **slideUp**: Fade in + slide up 30px
- **slideIn**: Fade in + slide in from left

## Responsive Design

### Mobile (< 768px)
- Single column layouts
- Sidebar hidden by default
- Full-width cards
- Reduced padding (1rem)
- Hamburger menu visible
- Tables scroll horizontally
- Stacked grids

### Tablet (768px - 1023px)
- 2 column grids
- Sidebar visible but narrow
- Medium padding (1.5rem)
- Responsive tables
- Flexible layouts

### Desktop (1024px+)
- Multi-column grids (3-4)
- Full sidebar (250px)
- Full padding (2rem)
- All features visible
- Optimized spacing

## Accessibility

### Contrast Ratios
- All text meets WCAG AA standards (4.5:1)
- Focus indicators visible
- Icon + text combinations
- Color not sole indicator

### Focus States
- Blue outline on focus
- Keyboard navigation supported
- Tab order logical
- Skip links implemented

### Semantic HTML
- Proper heading hierarchy (h1-h6)
- Semantic elements (nav, main, section)
- ARIA labels where needed
- Form labels associated

## Icon System

### Font Awesome 6.4
- Solid icons: `fas fa-*`
- Usage: `<i class="fas fa-icon-name"></i>`
- Size: Inherits from parent or `.fa-2x`, `.fa-3x`
- Color: Inherits from text color

### Common Icons
- Dashboard: `fas fa-home`
- Users: `fas fa-users`
- Courses: `fas fa-book`
- Results: `fas fa-chart-bar`
- Edit: `fas fa-edit`
- Delete: `fas fa-trash`
- Download: `fas fa-download`
- Settings: `fas fa-cog`

## Dark Mode Preparation

Ready for dark mode implementation:
- All colors use CSS variables
- Easy to swap variables
- High contrast maintained
- No inline styles to override

## Print Styles

Optimized for printing:
- Hide navigation elements
- Hide interactive elements
- Full width layout
- Black text on white
- No background colors

## CSS Variables Reference

```css
:root {
  --primary-color: #0d6efd;
  --secondary-color: #6c757d;
  --success-color: #198754;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #0dcaf0;
  --dark-color: #212529;
  --light-color: #f8f9fa;
  --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari 14+, Chrome Android)

## Performance Considerations

- CSS is minified and optimized
- Animations use GPU acceleration (transform)
- Images lazy-loaded where applicable
- No heavy JavaScript required
- Mobile-first approach

---

**Design System Version**: 1.0
**Last Updated**: November 10, 2025
**Status**: ✅ Production Ready
