/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
    content: [
        "./templates/**/*.html",
        // "./static/src/**/*.js",
    ],
    theme: {
        extend: {
            colors: {
                'c1': '#2A2B2A',
                'c2': '#374151',
                'c3': '#E04700',

            },
            fontFamily: {
                'sans': ['Inter var', ...defaultTheme.fontFamily.sans],
            },
        },
    },
    plugins: [],
}
