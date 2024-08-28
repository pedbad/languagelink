/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/templates/**/*.html',  // Add other paths as needed
  ],
  theme: {
    extend: {
      colors: {
        'warm-brown': 'var(--color-warm-brown)',
        'dark-orange': 'var(--color-dark-orange)',
        'vibrant-orange': 'var(--color-vibrant-orange)',
        'deep-teal': 'var(--color-deep-teal)',
        'bright-teal': 'var(--color-bright-teal)',
        'primary-dark-teal': 'var(--color-primary-dark-teal)',
        'secondary-slate-gray': 'var(--color-secondary-slate-gray)',
        'neutral-gray-brown': 'var(--color-neutral-gray-brown)',
        'accent-olive-green': 'var(--color-accent-olive-green)',
        'accent-bright-lime': 'var(--color-accent-bright-lime)',
      },
      margin: {
        '-150px': '-150px',
      },
    },
  },
  plugins: [],
}

