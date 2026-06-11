import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores(["dist", "node_modules", "src/**/*.js"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactRefresh.configs.vite,
    ],
    // eslint-plugin-react-hooks v7 ships its `recommended`/`recommended-latest`
    // configs with a legacy eslintrc-style `plugins: ["react-hooks"]` array,
    // which flat config rejects (the previous `extends` crashed ESLint before it
    // could lint anything). Register the plugin as an object and enable the
    // classic Rules of Hooks set directly. The newer opinionated v7 rules
    // (react-hooks/refs, react-hooks/set-state-in-effect) are intentionally not
    // enabled here yet — adopting them is tracked as follow-up code work.
    plugins: {
      "react-hooks": reactHooks,
    },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
    },
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
  },
]);
