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
              // The original SVG path had some issues; I've used a placeholder.
              // Please ensure your SVG path is correctly escaped for URL encoding.
              mask: `url("data:image/svg+xml;utf8,${encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.25 5.5a.75.75 0 0 0-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 0 0 .75-.75v-4a.75.75 0 0 1 1.5 0v4A2.25 2.25 0 0 1 12.75 17h-8.5A2.25 2.25 0 0 1 2 14.75v-8.5A2.25 2.25 0 0 1 4.25 4h5a.75.75 0 0 1 0 1.5h-5Z" clip-rule="evenodd" />
                  <path fill-rule="evenodd" d="M6.194 12.753a.75.75 0 0 0 1.06.053L16.5 4.44v2.81a.75.75 0 0 0 1.5 0v-4.5a.75.75 0 0 0-.75-.75h-4.5a.75.75 0 0 0 0 1.5h2.553l-9.056 8.194a.75.75 0 0 0-.053 1.06Z" clip-rule="evenodd" />
                </svg>
              `)}") no-repeat center / 100% 100%`,
              WebkitMask: `url("data:image/svg+xml;utf8,${encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="size-5">
                  <path fill-rule="evenodd" d="M4.25 5.5a.75.75 0 0 0-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 0 0 .75-.75v-4a.75.75 0 0 1 1.5 0v4A2.25 2.25 0 0 1 12.75 17h-8.5A2.25 2.25 0 0 1 2 14.75v-8.5A2.25 2.25 0 0 1 4.25 4h5a.75.75 0 0 1 0 1.5h-5Z" clip-rule="evenodd" />
                  <path fill-rule="evenodd" d="M6.194 12.753a.75.75 0 0 0 1.06.053L16.5 4.44v2.81a.75.75 0 0 0 1.5 0v-4.5a.75.75 0 0 0-.75-.75h-4.5a.75.75 0 0 0 0 1.5h2.553l-9.056 8.194a.75.75 0 0 0-.053 1.06Z" clip-rule="evenodd" />
                </svg>
              `)}")`,
              backgroundRepeat: 'no-repeat',
              backgroundSize: '100% 100%',
              backgroundColor: 'currentColor',
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
        'h3.form-heading': {
          '@apply text-primary-dark-teal text-lg font-light mb-1': {}
        },
        'hr.page-divider': {
          '@apply my-4 border-t border-primary-dark-teal border-opacity-30': {},
        },
      })
    },

    // form-field and form-control *base* styles
    function ({ addComponents }) {
      addComponents({
        // wrapper for each form field
        '.form-field': {
          '@apply mb-6 relative': {},
        },
        '.form-field + .form-field': {
          '@apply border-t border-primary-dark-teal border-opacity-30 pt-6': {}
        },
        // a tiny semantic helper instead of repeating "relative"
        '.floating-input': {
          '@apply relative': {},
        },
        // shared input/textarea styles (no floating-label or peer variants)
        '.form-control': {
          [
            `@apply block min-h-[auto] w-full rounded border border-gray-300 bg-white
              px-3 py-[0.32rem] leading-[2.15] outline-none
              focus:placeholder-transparent focus:border-primary-dark-teal focus:ring-primary-dark-teal`
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
          [base + ' text-xs px-2 py-1 bg-deep-teal text-white hover:bg-teal-600 focus:ring-primary-dark-teal']: {}
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
        /* Mini secondary (warm-brown) */
        '.btn-secondary-sm': {
          [ base +
            ' text-xs px-2 py-1 bg-warm-brown text-white' +
            ' hover:bg-dark-orange focus:ring-warm-brown'
          ]: {}
        },
        /* Cancel (gray) */
        '.btn-cancel': {
          [base + ' px-6 py-2 text-sm bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-400']: {}
        },
        /** Mini cancel (gray) */
        '.btn-cancel-sm': {
          [base +
            ' text-xs px-4 py-2 bg-gray-200 text-gray-800' +
            ' hover:bg-gray-300 focus:ring-gray-400'
          ]: {}
        },
        /* Danger (red) */
        '.btn-danger': {
          [base + ' px-4 py-2 text-sm bg-red-700 text-white hover:bg-red-600 focus:ring-red-500']: {}
        },
        /** Mini danger (red) */
        '.btn-danger-sm': {
          [base +
            ' text-xs px-2 py-1 bg-red-700 text-white' +
            ' hover:bg-red-600 focus:ring-red-500'
          ]: {}
        },
        /* Status: completed */
        '.btn-completed': {
          [base +
            ' px-3 py-1.5 bg-accent-olive-green text-white' +
            ' hover:bg-accent-bright-lime' +
            ' focus:ring-2 focus:ring-accent-olive-green focus:ring-opacity-50'
          ]: {}
        },
        /* Status: not-completed */
        '.btn-not-completed': {
          [base +
            ' px-3 py-1.5 bg-red-100 text-red-800' +
            ' hover:bg-red-200' +
            ' focus:ring-2 focus:ring-red-500 focus:ring-opacity-50'
          ]: {}
        },
        /* generic toggle button */
        '.btn-toggle': {
          [toggleBase]: {}
        },
        /* when currently ON, clicking DISABLES → red “danger” */
        '.btn-toggle-off': {
          ['@apply btn-toggle bg-[#B02907] hover:bg-[#992405] focus:ring-[#B02907] text-white']: {}
        },
        /* when currently OFF, clicking ENABLES → teal “primary” */
        '.btn-toggle-on': {
          ['@apply btn-toggle bg-[#10454F] hover:bg-[#0d3a45] focus:ring-[#10454F] text-white']: {}
        },
        /* wrapper around the student / teacher buttons on register page */
        '.btn-toggle-group': {
          '@apply inline-flex rounded-md shadow-sm': {}
        },
        /* each toggle button */
        '.btn-role-toggle': {
          '@apply relative inline-flex items-center px-3 py-2 text-sm font-semibold transition-colors duration-150 focus:z-10 focus:outline-none focus:ring-2 focus:ring-offset-2 rounded-none': {}
        },
        /* left edge (Student) */
        '.btn-role-toggle-left': {
          '@apply btn-role-toggle rounded-l-md': {}
        },
        /* right edge (Teacher) */
        '.btn-role-toggle-right': {
          '@apply btn-role-toggle rounded-r-md -ml-px': {}
        },
        /* when selected */
        '.btn-role-toggle-selected': {
          '@apply bg-deep-teal text-white ring-1 ring-inset ring-deep-teal hover:bg-teal-600': {}
        },
        /* when unselected */
        '.btn-role-toggle-unselected': {
          '@apply bg-white text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50': {}
        },
        /* Outline style for toggles */
        '.btn-outline': {
          '@apply inline-flex items-center justify-center px-4 py-2 rounded-lg bg-white text-gray-700 border border-gray-300 hover:bg-gray-100 focus:ring-gray-400': {}
        },
        /* Badge base */
        '.badge': {
          '@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium': {}
        },
        '.badge-primary-alt': {
          '@apply bg-white text-vibrant-orange': {}
        },
        '.badge-primary': {
          '@apply bg-white text-deep-teal': {}
        },
        '.badge-outline': {
          '@apply bg-gray-100 text-gray-500': {}
        }
      })
    },
  ],
}