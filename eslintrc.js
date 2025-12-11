module.exports = {
  env: {
    es2021: true,
    node: true,
    jest: true,
  },
  extends: [
    "eslint:recommended",
    "prettier", // disables rules that conflict with Prettier
  ],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "script",
  },
  rules: {
    noUnusedVars: "warn",       // warn on unused variables
    noUndef: "error",           // disallow undeclared variables
    noConsole: "off",           // allow console output (CLI tool)
    eqeqeq: "warn",             // encourage ===
    curly: "warn",              // require braces on blocks
  },
};
