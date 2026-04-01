# Architectural Documentation (UC1, UC2 & UC3 Standalone)

Bu doküman, projenin Use Case 1 (Team Builder), Use Case 2 (Points Calculator) ve Use Case 3 (Leaderboard) üzerine kurulu modüler yapısını özetler.

## 1. Event-Driven (Olay Tabanlı) Altyapı
Sistem, modüller arası iletişimi sağlamak için **Event-Driven Architecture (EDA)** prensiplerini kullanır. 

*   **[Core Event Bus]**: `core/event_bus.py` içerisinde tanımlıdır. Yayıncı-Abone (Pub-Sub) mantığıyla çalışır.
*   **[Data Events]**: Performans verileri yayımlandığında, UC2 (Scoring) tetiklenir ve sonuçları UC3 (Leaderboard) dinleyerek tabloyu gerçek zamanlı günceller.

## 2. Modüler (Modular) Mimari İskeleyi
Uygulama, **Modular Monolith** prensiplerine göre organize edilmiştir:

*   **[Use Case 1: Team Builder]**: `fantasy_team_usecase_1/` altında toplanmıştır.
*   **[Use Case 2: Points Calculator]**: `fantasy_points_usecase_2/` altında toplanmıştır.
*   **[Use Case 3: Leaderboard]**: `fantasy_leaderboard_usecase_3/` altında toplanmıştır. Sıralama yönetimini sağlar.

## 3. Katmanlı Mimari (Layered Architecture)
Her Use Case kendi içinde katmanlara ayrılmıştır:
- **Router Katmanı**: `router.py` (FastAPI bağlantısı).
- **Mantık Katmanı**: `team.py` / `calculator.py` / `leaderboard.py`.

## 4. Bağımsızlık ve Push Hazırlığı
Bu klasör (`standalone_uc1_uc2_uc3`), sistemin Veri Çekme (UC4) mekanizmasından tamamen arındırılmıştır. Sadece bu üç modülün kodlarını ve veritabanı altyapısını içerir, bu sayede temiz bir Git gönderimi yapılmasına olanak tanır.
