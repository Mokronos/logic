/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
    content: [
        "./templates/**/*.html",
        "./static/src/**/*.js",
    ],
    theme: {
        extend: {
            colors: {
                'primary': '#162B3C',
                'primary-light': '#31465E',
                'secondary': '#472C1B',
                'secondary-light': '#7D451B',
                'details': '#758E4F',

            },
            fontFamily: {
                'sans': ['Inter var', ...defaultTheme.fontFamily.sans],
            },
        },
    },
    plugins: [],
}
