// @ts-check
/** @type {import("eslint").Linter.Config} */
module.exports = {
    root: true,
    env: {
        browser: true,
        es2020: true,
    },
    extends: [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "prettier",
    ],
    ignorePatterns: ["dist", ".eslintrc.cjs", "node_modules"],
    parser: "@typescript-eslint/parser",
    parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
    },
    plugins: ["@typescript-eslint"],
    rules: {
        "@typescript-eslint/no-explicit-any": "warn",
        "@typescript-eslint/no-unused-vars": [
            "error",
            { argsIgnorePattern: "^_" },
        ],
        "no-console": "warn",
    },
};
