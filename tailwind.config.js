/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/templates/**/*.html',
    './users/templates/**/*.html',
    './booking/templates/**/*.html',
    './node_modules/tw-elements/dist/js/**/*.js',
  ],
  theme: {
    extend: {
      // ────────────────────────────────────────────────
      // ✨ TYPOGRAPHY OVERRIDES FOR .prose
      // ────────────────────────────────────────────────
      typography: (theme) => ({
        DEFAULT: {
          css: {
            a: {
              color: theme('colors.blue.600'),
              textDecoration: 'underline',
              '&:hover': {
                color: theme('colors.blue.800'),
              },
            },
            'a::after': {
              content: '""',
              display: 'inline-block',
              width: theme('spacing.4'),
              height: theme('spacing.4'),
              marginLeft: theme('spacing.1'),
              verticalAlign: 'middle',
              /* … your mask/svg stuff … */
            },
          },
        },
      }),
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
    require('@tailwindcss/typography'),

    // base overrides for page title & divider
    function ({ addBase }) {
      addBase({
        'h1.page-title': {
          '@apply text-3xl font-extralight text-gray-900 sm:text-4xl text-center mb-6': {},
        },
        'hr.page-divider': {
          '@apply my-4 border-t border-primary-dark-teal border-opacity-30': {},
        },
      })
    },

    // form-field, form-control and form-label *base* styles
    function ({ addComponents }) {
      addComponents({
        // wrapper for each form field
        '.form-field': {
          '@apply mb-6 relative': {},
        },
        // shared input/textarea styles (no peer-variants here!)
        '.form-control': {
          [ 
            `@apply block min-h-[auto] w-full rounded border border-gray-300 bg-white
             px-3 py-[0.32rem] leading-[2.15] outline-none transition-all
             duration-200 ease-linear placeholder-transparent`
          ]: {},
        },
        // shared floating-label styles (no peer-variants here!)
        '.form-label': {
          [
            `@apply pointer-events-none absolute left-3 top-0 mb-0 origin-[0_0] truncate
             pt-[0.37rem] leading-[2.15] text-neutral-500 transition-all
             duration-200 ease-out`
          ]: {},
        },
      })
    },

    // all your existing btn / badge / toggle components…
    function ({ addComponents }) {
      const base =
        '@apply inline-flex items-center justify-center whitespace-nowrap font-medium ' +
        'rounded-md transition-colors duration-150 shadow-md focus:outline-none ' +
        'focus:ring-4 focus:ring-opacity-60 cursor-pointer'
      const toggleBase =
        '@apply inline-flex items-center text-sm font-medium px-5 py-2 rounded-lg ' +
        'shadow-md transition-all duration-200 ease-linear focus:outline-none ' +
        'focus:ring-2 focus:ring-opacity-50 cursor-pointer'

      addComponents({
        '.btn':            { [base]: {} },
        '.btn-primary':    { [base + ' px-4 py-2 bg-deep-teal text-white hover:bg-teal-600 focus:ring-primary-dark-teal']: {} },
        '.btn-primary-lg': { [base + ' text-lg px-6 py-3 rounded-lg bg-deep-teal text-white hover:bg-teal-600 focus:ring-primary-dark-teal']: {} },
        '.btn-primary-sm': { [base + ' text-xs px-2 py-1 bg-deep-teal text-white hover:bg-teal-600 focus:ring-primary-dark-teal']: {} },
        /* …etc… */
        '.btn-toggle':     { [toggleBase]: {} },
        /* …etc… */
        '.badge':          { '@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium': {} },
        '.badge-primary':  { '@apply bg-white text-deep-teal': {} },
        '.badge-outline':  { '@apply bg-gray-100 text-gray-500': {} },
      })
    },
  ],
}
