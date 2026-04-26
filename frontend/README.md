# Frontend — Sistem Perencanaan Materi Adaptif & Pelaporan Otomatis
**Stack:** React TypeScript · RestFull API 

---

## Struktur Folder

```
frontend/
├── dist/                        ← Build output
├── node_modules/
├── public/
│   ├── assets/
│   ├── favicon.ico
│   ├── favicon.svg
│   └── icons.svg
├── src/
│   ├── App.css
│   ├── App.tsx
│   ├── index.css
│   ├── main.tsx
│   ├── styles.ts
│   ├── assets/
│   │   ├── css/
│   │   ├── images/
│   │   ├── js/
│   │   ├── media/
│   │   └── plugins/
│   ├── components/
│   │   ├── colorstyle.ts
│   │   ├── fontstyle.ts
│   │   ├── footer.tsx
│   │   ├── header.tsx
│   │   ├── sidebar-old.tsx
│   │   ├── sidebar.tsx
│   │   ├── styles.ts
│   │   └── tablestyle.ts
│   ├── config-route/
│   │   ├── NavigationContext.tsx
│   │   └── UseNavigation.ts
│   ├── data/
│   │   ├── images.tsx
│   │   └── index.tsx
│   ├── layout/
│   │   └── MainLayout-tx.tsx
│   ├── pages/
│   │   ├── daily-log/
│   │   │   ├── components/
│   │   │   ├── daily-log-index/
│   │   │   ├── detail-log-siswa/
│   │   │   ├── form/
│   │   │   ├── form-makul/
│   │   │   ├── index.tsx
│   │   │   ├── list-siswa/
│   │   │   └── useDailyLog.ts
│   │   ├── daily-log copy/
│   │   │   ├── components/
│   │   │   ├── daily-log-index/
│   │   │   ├── detail-log-siswa/
│   │   │   ├── form/
│   │   │   ├── form-makul/
│   │   │   ├── index.tsx
│   │   │   └── list-siswa/
│   │   ├── dashboard/
│   │   │   ├── ActivityItem.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── StatCardItem.tsx
│   │   │   ├── statCards.tsx
│   │   │   ├── studentRow.tsx
│   │   │   └── useDashboard.ts
│   │   ├── detail-kelas/
│   │   │   ├── index.tsx
│   │   │   ├── styles.ts
│   │   │   └── useGenerateReport.ts
│   │   ├── detail-log-siswa/
│   │   │   ├── index.tsx
│   │   │   ├── styles.ts
│   │   │   └── useDailyLogSiswa.ts
│   │   ├── form-daily-log/
│   │   │   ├── index.tsx
│   │   │   ├── styles.ts
│   │   │   └── useDailyLog.ts
│   │   ├── learning-plan/
│   │   │   ├── constants.tsx
│   │   │   ├── index.tsx
│   │   │   ├── plan-detail/
│   │   │   ├── plan-detail-data/
│   │   │   ├── types.tsx
│   │   │   └── useLearningPlan.ts
│   │   ├── learning-plan-old/
│   │   ├── login/
│   │   ├── master-kelas/
│   │   │   ├── index.tsx
│   │   │   ├── styles.ts
│   │   │   └── useKelasApi.ts
│   │   ├── master-mapel/
│   │   │   ├── index.tsx
│   │   │   ├── styles.ts
│   │   │   └── useMapelApi.ts
│   │   ├── master-siswa/
│   │   │   ├── index.tsx
│   │   │   ├── styles.ts
│   │   │   └── useSiswaApi.ts
│   │   ├── plan-detail/
│   │   │   ├── index.tsx
│   │   │   └── useLearningPlan.ts
│   │   └── report-editor/
│   │       ├── constants.tsx
│   │       ├── index.tsx
│   │       ├── types.tsx
│   │       └── useReport.ts
│   ├── service/
│   │   ├── apiFetch.ts
│   │   ├── apiUrl.ts
│   │   ├── authService.ts
│   │   ├── dailyLogAPI.ts
│   │   ├── dashboardAPI.ts
│   │   ├── kelasAPI.ts
│   │   ├── mapelAPI.ts
│   │   ├── payload.ts
│   │   ├── planAPI.ts
│   │   ├── reportAPI.ts
│   │   └── siswaAPI.ts
│   ├── types/
│   │   └── index.tsx
│   └── ui/
│       ├── ActivityItem.tsx
│       ├── Notifications.tsx
│       ├── StatCardItem.tsx
│       └── StudentRow.tsx
├── Dockerfile
├── eslint.config.js
├── index.html
├── package-lock.json
├── package.json
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts

