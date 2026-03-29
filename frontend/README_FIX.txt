This frontend fix adds:
- tsconfig path alias support for @/*
- next-env.d.ts
- postcss.config.js
- tailwind.config.js

The previous build error:
Module not found: Can't resolve '@/components/LinkForm'
was caused by missing path alias setup in frontend/tsconfig.json.
