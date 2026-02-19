# ISC-CORE CI Policy

Bu repo private olabilir; GitHub "branch protection" zorla uygulamayabilir.
Bu yüzden tek otorite CI'dir.

## Merge / kabul şartları
- `vectors` job'u PASS olmalı
- `tools/ci_policy.sh` EXIT 0 olmalı
- `tools/ci_report_hash_check.py` OK olmalı (CI_REPORT_V1)
- `tools/phi_tripwire.sh` OK olmalı (Truth Layer içinde phi yasak)

## Operasyon kuralı
- main'e direkt push yerine PR açılır
- kırmızı CI = merge yok
