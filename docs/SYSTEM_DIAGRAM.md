# Survey System - Architecture Diagram

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│  (Tailwind CSS + HTMX + Font Awesome + Chart.js)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO APPLICATION                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   accounts   │  │  dashboard   │  │  manajemen   │        │
│  │ (Auth/User)  │  │   (Views)    │  │(Permissions) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────────────────────────┐       │
│  │ api_simpeg   │  │       survey_jpt                 │       │
│  │ (Pegawai)    │  │  (Dynamic Survey System)         │       │
│  └──────────────┘  └──────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │    MySQL     │  │    Redis     │  │  Static Files│        │
│  │  (Database)  │  │ (Cache/Sess) │  │  (Whitenoise)│        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Database Schema Relationships

```
┌─────────────────────┐
│   survey_jenis      │
│  (Master Survey)    │
│                     │
│  - id (PK)          │
│  - kode (unique)    │
│  - nama             │
│  - deskripsi        │
│  - is_active        │
└──────────┬──────────┘
           │ 1
           │
           │ N
┌──────────▼──────────┐
│ survey_pertanyaan   │
│  (Questions)        │
│                     │
│  - id (PK)          │
│  - jenis_survey_id  │◄─────┐
│  - kode_pertanyaan  │      │
│  - pertanyaan       │      │
│  - urutan           │      │
│  - bobot            │      │
│  - is_active        │      │
└──────────┬──────────┘      │
           │                  │
           │ N                │
           │                  │
           │                  │
┌──────────▼──────────┐      │
│  survey_jawaban     │      │
│   (Answers)         │      │
│                     │      │
│  - id (PK)          │      │
│  - responden_id     │◄─┐   │
│  - pertanyaan_id    │──┘   │
│  - nilai (1-5)      │      │
└─────────────────────┘      │
           ▲                  │
           │ N                │
           │                  │
           │ 1                │
┌──────────┴──────────┐      │
│ survey_responden    │      │
│  (Respondents)      │      │
│                     │      │
│  - id (PK)          │      │
│  - id_pegawaiPenilai│      │
│  - nip_pegawaiPenilai│     │
│  - id_pegawaiDinilai│      │
│  - nip_pegawaiDinilai│     │
│  - peranPenilai     │      │
│  - statusData       │      │
└─────────────────────┘      │
                              │
                              │
┌─────────────────────┐      │
│ api_simpeg_pegawai  │      │
│  (Employee Data)    │      │
│                     │      │
│  - id (PK)          │      │
│  - nip              │──────┘
│  - nama             │  (Reference)
│  - data_pegawai     │
│  - statusData       │
└─────────────────────┘
```

## 🔄 Survey Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADMIN: Setup Survey                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Create Jenis   │
                    │     Survey      │
                    │  (JPT, 360)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Add Pertanyaan  │
                    │  (Questions)    │
                    │  + Set Bobot    │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER: Input Penilaian                        │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Select Pegawai  │
                    │   yang Dinilai  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Fill Survey    │
                    │  Form (1-5)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Save Jawaban   │
                    │  + Calculate    │
                    │  Weighted Score │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM: Generate Report                      │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Aggregate Data │
                    │  by Pegawai     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Show Charts    │
                    │  & Statistics   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Export Report  │
                    │  (Excel/PDF)    │
                    └─────────────────┘
```

## 🎯 Menu Navigation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         SIDEBAR MENU                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌───────────────────┐       ┌───────────────────┐
    │   📊 Survey       │       │ 🔧 Manajemen      │
    │   (Category 7)    │       │    Integrasi      │
    └───────┬───────────┘       │ (Category 4)      │
            │                   └───────┬───────────┘
            │                           │
    ┌───────┴───────┐                   │
    │               │                   ▼
    ▼               ▼           ┌───────────────┐
┌─────────┐   ┌─────────┐      │  📡 ESIMPEG   │
│Penilaian│   │ Master  │      │   (Parent)    │
│   JPT   │   │ Survey  │      └───────┬───────┘
│(Parent) │   │(Parent) │              │
└────┬────┘   └────┬────┘              ▼
     │             │              ┌─────────────┐
     │             │              │ 👥 Pegawai  │
     │             │              │   (Child)   │
     │             │              └─────────────┘
     │             │
     ▼             ▼
┌─────────┐   ┌─────────┐
│ Daftar  │   │ Jenis   │ ← ANSWER: "jenis survey tu mana dia"
│Penilaian│   │ Survey  │   LOCATION: Survey → Master Survey → Jenis Survey
└─────────┘   └─────────┘   URL: /admin/survey_jpt/jenissurvey/
┌─────────┐   ┌─────────┐
│ Tambah  │   │Pertanyaan│
│Penilaian│   │ Survey  │
└─────────┘   └─────────┘
┌─────────┐
│ Laporan │
│  Hasil  │
└─────────┘
```

## 🔢 Calculation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEIGHTED SCORING SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

Input: User fills survey form
┌─────────────────────────────────────────────────────────────────┐
│  Pertanyaan 1: Nilai = 5, Bobot = 1.0                         │
│  Pertanyaan 2: Nilai = 4, Bobot = 1.5                         │
│  Pertanyaan 3: Nilai = 5, Bobot = 2.0                         │
│  Pertanyaan 4: Nilai = 3, Bobot = 1.0                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Calculate: nilai_terbobot = nilai × bobot
┌─────────────────────────────────────────────────────────────────┐
│  Pertanyaan 1: 5 × 1.0 = 5.0                                   │
│  Pertanyaan 2: 4 × 1.5 = 6.0                                   │
│  Pertanyaan 3: 5 × 2.0 = 10.0                                  │
│  Pertanyaan 4: 3 × 1.0 = 3.0                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Aggregate: Total & Average
┌─────────────────────────────────────────────────────────────────┐
│  Total Nilai Terbobot = 5.0 + 6.0 + 10.0 + 3.0 = 24.0         │
│  Total Bobot = 1.0 + 1.5 + 2.0 + 1.0 = 5.5                    │
│  Rata-rata = 24.0 / 5.5 = 4.36                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
Output: Final Score
┌─────────────────────────────────────────────────────────────────┐
│  Pegawai: [Nama Pegawai]                                       │
│  Jenis Survey: JPT                                             │
│  Total Nilai: 24.0                                             │
│  Rata-rata: 4.36 / 5.0                                         │
│  Kategori: Sangat Baik (> 4.0)                                │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 UI Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                      base_dashboard.html                        │
│  (Sidebar + Header + Content Area)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │  Sidebar  │  │  Header   │  │  Content  │
        │  (Green-  │  │  (Solid   │  │   Area    │
        │   Teal)   │  │ Gradient) │  │           │
        └───────────┘  └───────────┘  └─────┬─────┘
                                             │
                              ┌──────────────┼──────────────┐
                              │              │              │
                              ▼              ▼              ▼
                        ┌──────────┐  ┌──────────┐  ┌──────────┐
                        │Dashboard │  │  Survey  │  │   API    │
                        │  Index   │  │  Views   │  │ SIMPEG   │
                        └──────────┘  └──────────┘  └──────────┘
                              │              │              │
                              │              │              │
                              ▼              ▼              ▼
                        ┌──────────┐  ┌──────────┐  ┌──────────┐
                        │  Stats   │  │  Forms   │  │  Table   │
                        │  Cards   │  │  (HTMX)  │  │(django-  │
                        │ (Animated)│  │          │  │ tables2) │
                        └──────────┘  └──────────┘  └──────────┘
```

## 🔐 Permission Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LOGIN                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Authenticate   │
                    │  (Session)      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Load User       │
                    │ Permissions     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Build Dynamic   │
                    │ Sidebar Menu    │
                    │ (Based on Perms)│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Show Only       │
                    │ Allowed Menus   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Check Permission│
                    │ on Each Request │
                    └─────────────────┘
```

---

**Note**: All diagrams are simplified representations. Actual implementation may have additional components and relationships.
