/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/templates/**/*.html',
    './users/templates/**/*.html',
    './booking/templates/**/*.html',
    './node_modules/tw-elements/dist/js/**/*.js'
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
  plugins: [
  function ({ addComponents }) {
    const base = '@apply inline-flex items-center justify-center whitespace-nowrap font-medium rounded-md transition-colors duration-150 shadow-md focus:outline-none focus:ring-4 focus:ring-opacity-60';
    addComponents({
      /* Base shape */
      '.btn': {
        [base]: {}
      },
      /* Primary (default) */
      '.btn-primary': {
        [base + ' px-4 py-2 bg-deep-teal text-white hover:bg-teal-600 focus:ring-primary-dark-teal']: {}
      },
      /* Primary, large */
      '.btn-primary-lg': {
        [base + ' text-lg px-6 py-3 rounded-lg bg-deep-teal text-white hover:bg-teal-600 focus:ring-primary-dark-teal']: {}
      },
      /* Mini (for tiny text-xs buttons) */
      '.btn-primary-sm': {
        [base + ' text-xs px-4 py-2 bg-deep-teal text-white hover:bg-teal-600 focus:ring-primary-dark-teal']: {}
      },
      /* Alt-primary (orange) */
      '.btn-primary-alt': {
        [base + ' px-4 py-2 bg-vibrant-orange text-white hover:bg-dark-orange focus:ring-vibrant-orange']: {}
      },
      /* Alt-primary, large */
      '.btn-primary-alt-lg': {
        [base + ' text-lg px-6 py-3 rounded-lg bg-vibrant-orange text-white hover:bg-dark-orange focus:ring-vibrant-orange']: {}
      },
      /* Secondary (warm-brown) */
      '.btn-secondary': {
        [base + ' px-6 py-2 text-sm bg-warm-brown text-white hover:bg-dark-orange focus:ring-warm-brown']: {}
      },
      /* Cancel (gray) */
      '.btn-cancel': {
        [base + ' px-6 py-2 text-sm bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400']: {}
      },
      /* Danger (red) */
      '.btn-danger': {
        [base + ' px-4 py-2 text-sm bg-red-700 text-white hover:bg-red-600 focus:ring-red-500']: {}
      }
    })
  }
]
}
