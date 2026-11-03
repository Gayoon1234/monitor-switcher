---
id: index
title: Monitor Switcher documentation
slug: /
sidebar_position: 0
---

Monitor Switcher is a Windows desktop application that switches monitor inputs based on USB device connection events.

## Documentation areas

- [Technical implementation](technical-implementation.md)
- [CLI](cli/index.md)
- [Hardware](hardware/index.md)
- [Services](services/index.md)
- [UI](ui/index.md)

## Develop the documentation

Install and run the documentation site from the repository root on Windows:

```powershell
cd docs
npm install
npm start
```

Create a production build with:

```powershell
npm run build
```

The generated static site is written to `docs/build/`.
