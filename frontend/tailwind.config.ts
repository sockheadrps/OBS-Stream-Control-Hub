import type { Config } from 'tailwindcss';
import flowbitePlugin from 'flowbite/plugin'
import daisyui from 'daisyui'
import containerQueries from '@tailwindcss/container-queries';
import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';

export default {
  content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flowbite-svelte/**/*.{html,js,svelte,ts}',"./node_modules/flowbite-svelte-icons/**/*.{html,js,svelte,ts}"],
  darkMode: 'media', // Changed from 'class' to 'media' for default dark mode
  theme: {
    extend: {
      colors: {
        // flowbite-svelte
        primary: {
          50: '#FFF5F2',
          100: '#FFF1EE',
          200: '#FFE4DE',
          300: '#FFD5CC',
          400: '#FFBCAD',
          500: '#FE795D',
          600: '#EF562F',
          700: '#EB4F27',
          800: '#CC4522',
          900: '#A5371B'
        }
      }
    }
  },
  
  
	plugins: [typography, forms, containerQueries, flowbitePlugin, daisyui]

} as Config;